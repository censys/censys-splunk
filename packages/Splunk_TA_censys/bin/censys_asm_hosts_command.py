# encoding = utf-8
#
# Two modes (see stream()): Splunk passes an iterator of records into stream().
#
#   NOT PIPED IN — bounded materialization of records yields an empty list.
#     With ip= set: | censysasmhosts ip="192.0.2.1,192.0.2.2" — standalone ASM fetch.
#       ip= is comma-separated; ip_field is ignored. Each successful GET is a NEW event (_raw = JSON).
#     With no ip= and empty upstream: yield zero rows (no error); ASM API key is not loaded.
#
#   PIPED IN — one or more upstream events.
#     Example: | ... | censysasmhosts ip_field=riskIP
#     Read the lookup address from each row: record[ip_field] or fallback record["ip"].
#     Same rows are passed through; we only add/set seed and host_ip (ASM enrichment).
#     Original fields (e.g. ip, riskIP) are not cleared — only seed and host_ip are written.
#
#     Pipeline progress uses stderr (see _report_progress). Splunk may label those lines ERROR in
#     logs; the text ``progress:`` means informational—not a command failure.
#
#     Optional throttling when piped (defaults batch_size=20 batch_delay=10):
#       batch_size 1–100 — max parallel ASM GETs per batch; use 1 for strictly sequential batches.
#       batch_delay 0–60 — whole seconds to sleep after each batch; 0 = no sleep.
#     Optional proxy= for v1/assets/hosts GETs (e.g. http://host:port); same URL used for http/https.
#     Each distinct IP causes at most one ASM host GET per search (piped or ip= list).
#     Piped input is capped (MAX_PIPELINE_RECORDS) so the command does not buffer unbounded rows.

import json
import sys
import threading
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple

import requests
import splunk_ta_censys_declare

from splunklib.searchcommands import Configuration, dispatch, Integer, Option
from splunklib.searchcommands import StreamingCommand
from splunklib.client import Service

BASE_URL = "https://app.censys.io/api"
DEFAULT_REALM = "censys_setup"
DEFAULT_SECRET_NAME = "censys_secrets"
SECRET_KEY_ASM_API = "censys_asm_api_key"
HOSTS_SOURCETYPE = "censys:asm:hosts"
HOSTS_SOURCE = "censys_asm_hosts"

# Piped mode only: defaults and bounds for batch_size / batch_delay (whole seconds).
DEFAULT_BATCH_SIZE = 20
DEFAULT_BATCH_DELAY = 10
MIN_BATCH_SIZE = 1
MAX_BATCH_SIZE = 100
MAX_BATCH_DELAY_SEC = 60
# Piped mode: max events buffered in memory (fail fast if upstream returns more).
MAX_PIPELINE_RECORDS = 50_000
# Per-request timeout for GET .../v1/assets/hosts/{ip} (connect + read, seconds).
ASM_HOST_GET_TIMEOUT_SEC = 5

# ThreadPoolExecutor workers may log fetch failures concurrently; keep stderr lines intact.
_FETCH_ERR_LOG_LOCK = threading.Lock()


def _materialize_records_bounded(records: Iterable[dict]) -> List[dict]:
    """Collect pipeline records up to MAX_PIPELINE_RECORDS; raise if the stream is larger."""
    out: List[dict] = []
    for i, rec in enumerate(records):
        if i >= MAX_PIPELINE_RECORDS:
            raise ValueError(
                f"Piped input exceeds the maximum of {MAX_PIPELINE_RECORDS:,} events. "
                "Use a narrower search (time range, filters, head) or split into multiple runs."
            )
        out.append(rec)
    return out


def get_asm_api_key(service: Service) -> str:
    """Get Censys ASM API key from storage (censys_setup realm)."""
    for password in service.storage_passwords:
        if (
            password.realm == DEFAULT_REALM
            and password.username == DEFAULT_SECRET_NAME
            and password.clear_password
        ):
            try:
                secrets = json.loads(password.clear_password)
                key = secrets.get(SECRET_KEY_ASM_API)
                if key:
                    return key
            except json.JSONDecodeError:
                pass
    raise ValueError(
        "Censys ASM API key not found. Configure it in the Censys add-on or censys-setup."
    )


def _is_blank(value: Any) -> bool:
    if value is None:
        return True
    s = str(value).strip()
    return not s or s.lower() == "null"


def _seed_from_discovery_trail(trail: Any) -> str:
    """Return seed assetId from discoveryTrail, or ""."""
    if not trail or not isinstance(trail, list):
        return ""
    for entry in trail:
        if not isinstance(entry, dict):
            continue
        is_seed = entry.get("isSeed")
        if is_seed is True or str(is_seed).lower() == "true" or str(is_seed) == "1":
            asset_id = entry.get("assetId")
            return asset_id if asset_id is not None else ""
    return ""


def _host_primary_ip(host: Dict[str, Any], fallback: str) -> str:
    return host.get("ip") or host.get("ipAddress") or fallback


def _report_error(cmd_name: str, exc: Exception) -> None:
    """Write error and traceback to stderr for Job Inspector / splunkd.log."""
    sys.stderr.write(f"{cmd_name} error: {exc!r}\n")
    traceback.print_exc(file=sys.stderr)
    sys.stderr.flush()


def _report_progress(cmd_name: str, message: str) -> None:
    """Emit pipeline status on stderr (same transport Splunk uses for command diagnostics).

    NOT A FAILURE: Lines are informational only (prefix ``progress:``). Splunk's
    ChunkedExternProcessorStderrLogger still records *all* stderr from extern
    commands at ERROR severity—operators should ignore that level for lines
    that start with ``<cmd> progress:`` and treat ``<cmd> error:`` as real errors.
    """
    sys.stderr.write(f"{cmd_name} progress: {message}\n")
    sys.stderr.flush()


def _report_fetch_error(cmd_name: str, ip: str, exc: BaseException) -> None:
    """One line per failed ASM host GET (HTTP/network/JSON). Blank IPs never call this."""
    detail = str(exc)
    if isinstance(exc, requests.HTTPError) and exc.response is not None:
        detail = f"HTTP {exc.response.status_code} {detail}"
    line = f"{cmd_name} fetch error: ip={ip!r} {detail}\n"
    with _FETCH_ERR_LOG_LOCK:
        sys.stderr.write(line)
        sys.stderr.flush()


@Configuration()
class CensysAsmHostsCommand(StreamingCommand):
    """
    Fetch host asset(s) from Censys ASM by IP (GET .../v1/assets/hosts/{ip}).

    Optional proxy= forwards those GETs through the given proxy URL.

    Not piped + ip=: | censysasmhosts ip="..."  →  new events per host.
    Not piped, no ip=, empty upstream →  zero rows (not an error).
    Piped: | ... | censysasmhosts →  enrich each row (seed, host_ip only).
    """

    # Used only when NOT piped in (standalone search). Ignored when upstream events exist.
    ip = Option(
        doc="IP address(es) when not using pipeline input (comma-separated)."
    )
    # Used only when piped in: which field on each event holds the IP to look up.
    ip_field = Option(
        default="ip",
        doc="Field on piped events with the IP (e.g. riskIP).",
    )
    batch_size = Option(
        default=DEFAULT_BATCH_SIZE,
        validate=Integer(MIN_BATCH_SIZE, MAX_BATCH_SIZE),
        doc=(
            "When piped in: max parallel ASM host GETs per batch (%d–%d). "
            "Use %d for one IP per batch (minimal parallelism). Default: %d."
            % (MIN_BATCH_SIZE, MAX_BATCH_SIZE, MIN_BATCH_SIZE, DEFAULT_BATCH_SIZE)
        ),
    )
    batch_delay = Option(
        default=DEFAULT_BATCH_DELAY,
        validate=Integer(0, MAX_BATCH_DELAY_SEC),
        doc=(
            "When piped in: seconds to sleep after each batch (%d–%d). "
            "0 = no delay. Default: %d."
            % (0, MAX_BATCH_DELAY_SEC, DEFAULT_BATCH_DELAY)
        ),
    )
    proxy = Option(
        doc=(
            "Optional proxy URL for ASM host GETs (e.g. http://proxy.example.com:8080). "
            "Applied to https://app.censys.io/... requests; omit to use direct connections."
        ),
    )

    # --- Shared: HTTP + JSON fetch (both modes) ---

    def _requests_proxies(self) -> Optional[Dict[str, str]]:
        if _is_blank(self.proxy):
            return None
        url = str(self.proxy).strip()
        return {"http": url, "https": url}

    def _request_headers(self) -> Dict[str, str]:
        api_key = get_asm_api_key(self.service)
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Censys-Api-Key": api_key,
        }

    def _fetch_host_json(self, ip: str, headers: Dict[str, str]) -> Tuple[Optional[dict], bool]:
        """Returns (host_json, failed). failed True means skip / use empty enrichment."""
        if _is_blank(ip):
            return None, True
        url = f"{BASE_URL}/v1/assets/hosts/{ip}"
        try:
            r = requests.get(
                url,
                headers=headers,
                timeout=ASM_HOST_GET_TIMEOUT_SEC,
                proxies=self._requests_proxies(),
            )
            r.raise_for_status()
            return r.json(), False
        except requests.RequestException as e:
            _report_fetch_error("censysasmhosts", ip, e)
            return None, True
        except json.JSONDecodeError as e:
            _report_fetch_error("censysasmhosts", ip, e)
            return None, True

    # --- NOT piped in: build brand-new Splunk events from ASM (full host in _raw) ---

    def _yield_standalone_host_event(self, host: dict, requested_ip: str) -> dict:
        raw = json.dumps(host)
        trail = host.get("discoveryTrail")
        event = {
            "_raw": raw,
            "sourcetype": HOSTS_SOURCETYPE,
            "source": HOSTS_SOURCE,
            "output_mode": "json",
            "ip": _host_primary_ip(host, requested_ip),
            "seed": _seed_from_discovery_trail(trail),
        }
        if trail is not None:
            event["discoveryTrail"] = json.dumps(trail)
        return event

    # --- Piped in: mutate each incoming record; only touch seed + host_ip ---

    def _clear_enrichment_fields(self, record: dict) -> None:
        # Empty ASM enrichment only. Does not remove ip, ip_field, or other piped columns.
        self.add_field(record, "seed", "")
        self.add_field(record, "host_ip", "")

    def _apply_asm_to_record(self, record: dict, host: dict, requested_ip: str) -> None:
        trail = host.get("discoveryTrail")
        self.add_field(record, "host_ip", _host_primary_ip(host, requested_ip))
        self.add_field(record, "seed", _seed_from_discovery_trail(trail))

    def _enrich_record_from_cache(
        self, record: dict, ip: str, cache: Dict[str, Tuple[Optional[dict], bool]]
    ) -> dict:
        host, failed = cache[ip]
        if failed or not host:
            self._clear_enrichment_fields(record)
        else:
            self._apply_asm_to_record(record, host, ip)
        return record

    def _flush_pending_batch(
        self,
        pending: List[Tuple[dict, str]],
        headers: Dict[str, str],
        batch_size: int,
        ip_cache: Dict[str, Tuple[Optional[dict], bool]],
    ) -> Iterator[dict]:
        """One GET per distinct IP in pending; yield one row per pending record."""
        if not pending:
            return
        unique_ips: List[str] = []
        seen: set = set()
        for _, ip in pending:
            if ip not in seen:
                seen.add(ip)
                unique_ips.append(ip)
        workers = min(len(unique_ips), batch_size)
        with ThreadPoolExecutor(max_workers=workers) as pool:
            fetched = list(
                pool.map(lambda i: self._fetch_host_json(i, headers), unique_ips)
            )
        for ip, pair in zip(unique_ips, fetched):
            ip_cache[ip] = pair
        for record, ip in pending:
            yield self._enrich_record_from_cache(record, ip, ip_cache)
        pending.clear()

    def _stream_without_pipeline(self, headers: Dict[str, str]) -> Iterator[dict]:
        # No upstream events: require ip=, split list, one GET per address, yield new rows.
        if _is_blank(self.ip):
            raise ValueError(
                "The ip option is required when no events are piped in "
                "(calls api/v1/assets/hosts/{ip})"
            )
        raw_ips = [
            s.strip()
            for s in str(self.ip).split(",")
            if s and s.strip().lower() != "null"
        ]
        seen_ip: set = set()
        ips: List[str] = []
        for ip in raw_ips:
            if ip not in seen_ip:
                seen_ip.add(ip)
                ips.append(ip)
        if not ips:
            raise ValueError("The ip option must contain at least one IP address")
        for ip in ips:
            host, failed = self._fetch_host_json(ip, headers)
            if not failed and host:
                yield self._yield_standalone_host_event(host, ip)

    def _stream_with_pipeline(
        self, records: List[dict], headers: Dict[str, str]
    ) -> Iterator[dict]:
        # Upstream events: read IP per row, optional batching + delay, yield same records enriched.
        ip_field = (self.ip_field or "ip").strip() or "ip"
        batch_sz = self.batch_size
        if batch_sz is None:
            batch_sz = DEFAULT_BATCH_SIZE
        delay_sec = self.batch_delay
        if delay_sec is None:
            delay_sec = DEFAULT_BATCH_DELAY

        pending: List[Tuple[dict, str]] = []
        ip_cache: Dict[str, Tuple[Optional[dict], bool]] = {}
        total_records = len(records)
        records_with_ip = 0
        for rec in records:
            rec_ip = rec.get(ip_field) or rec.get("ip")
            if not _is_blank(rec_ip):
                records_with_ip += 1

        total_batches = (
            (records_with_ip + batch_sz - 1) // batch_sz if records_with_ip > 0 else 0
        )

        _report_progress(
            "censysasmhosts",
            f"pipeline start: records={total_records}, batches={total_batches}",
        )

        batch_num = 0

        for record in records:
            raw_ip = record.get(ip_field) or record.get("ip")
            if _is_blank(raw_ip):
                self._clear_enrichment_fields(record)
                yield record
                continue

            ip = str(raw_ip).strip()
            if ip in ip_cache:
                yield self._enrich_record_from_cache(record, ip, ip_cache)
                continue

            pending.append((record, ip))
            if len(pending) >= batch_sz:
                yield from self._flush_pending_batch(
                    pending, headers, batch_sz, ip_cache
                )
                batch_num += 1
                _report_progress(
                    "censysasmhosts",
                    f"batch complete: {batch_num}/{total_batches}",
                )
                if delay_sec > 0:
                    time.sleep(delay_sec)

        n_final = len(pending)
        yield from self._flush_pending_batch(pending, headers, batch_sz, ip_cache)
        if n_final > 0:
            batch_num += 1
            _report_progress(
                "censysasmhosts",
                f"batch complete: {batch_num}/{total_batches}",
            )

    def stream(self, records):
        # Materialize input first (no API key yet) so empty upstream + no ip= can exit without auth.
        try:
            records_list = _materialize_records_bounded(records)
        except Exception as e:
            _report_error("censysasmhosts", e)
            raise

        if not records_list and _is_blank(self.ip):
            return

        try:
            headers = self._request_headers()
        except Exception as e:
            _report_error("censysasmhosts", e)
            raise

        try:
            if not records_list:
                yield from self._stream_without_pipeline(headers)
            else:
                yield from self._stream_with_pipeline(records_list, headers)
        except Exception as e:
            _report_error("censysasmhosts", e)
            raise


dispatch(CensysAsmHostsCommand, sys.argv, sys.stdin, sys.stdout, __name__)
