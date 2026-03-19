# encoding = utf-8
#
# Two modes (see stream()): Splunk passes an iterator of records into stream().
#
#   NOT PIPED IN — records_list is empty after list(records).
#     Example: | censysasmhosts ip="192.0.2.1,192.0.2.2"
#     Use the ip= option (comma-separated). ip_field is ignored.
#     Each successful API response becomes a NEW event (_raw = full host JSON).
#
#   PIPED IN — one or more upstream events.
#     Example: | ... | censysasmhosts ip_field=riskIP
#     Read the lookup address from each row: record[ip_field] or fallback record["ip"].
#     Same rows are passed through; we only add/set domain and host_ip (ASM enrichment).
#     Original fields (e.g. ip, riskIP) are not cleared — only domain and host_ip are written.
#
#     Pipeline progress uses stderr (see _report_progress). Splunk may label those lines ERROR in
#     logs; the text ``progress:`` means informational—not a command failure.
#
#     Optional throttling when piped (defaults batch_size=20 batch_delay=10):
#       batch_size=0   — no batching (one request at a time per event).
#       batch_delay=0  — no sleep between batches.

import json
import sys
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, Iterator, List, Optional, Tuple

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

# Piped mode only: defaults for optional batch_size / batch_delay (whole seconds).
DEFAULT_BATCH_SIZE = 20
DEFAULT_BATCH_DELAY = 10


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


def _domain_from_discovery_trail(trail: Any) -> str:
    """Return seed DOMAIN_NAME assetId from discoveryTrail, or ""."""
    if not trail or not isinstance(trail, list):
        return ""
    for entry in trail:
        if not isinstance(entry, dict) or entry.get("type") != "DOMAIN_NAME":
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
    sys.stderr.write(f"{cmd_name} fetch error: ip={ip!r} {detail}\n")
    sys.stderr.flush()


@Configuration()
class CensysAsmHostsCommand(StreamingCommand):
    """
    Fetch host asset(s) from Censys ASM by IP (GET .../v1/assets/hosts/{ip}).

    Not piped: | censysasmhosts ip="..."  →  new events per host.
    Piped:    | ... | censysasmhosts      →  enrich each row (domain, host_ip only).
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
        validate=Integer(0),
        doc=(
            "When piped in: max parallel ASM host GETs per batch. "
            "0 = no batching (sequential). Default: %d." % DEFAULT_BATCH_SIZE
        ),
    )
    batch_delay = Option(
        default=DEFAULT_BATCH_DELAY,
        validate=Integer(0),
        doc=(
            "When piped in: seconds to sleep after each batch. "
            "0 = no delay. Default: %d." % DEFAULT_BATCH_DELAY
        ),
    )

    # --- Shared: HTTP + JSON fetch (both modes) ---

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
            r = requests.get(url, headers=headers, timeout=30)
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
            "domain": _domain_from_discovery_trail(trail),
        }
        if trail is not None:
            event["discoveryTrail"] = json.dumps(trail)
        return event

    # --- Piped in: mutate each incoming record; only touch domain + host_ip ---

    def _clear_enrichment_fields(self, record: dict) -> None:
        # Empty ASM enrichment only. Does not remove ip, ip_field, or other piped columns.
        self.add_field(record, "domain", "")
        self.add_field(record, "host_ip", "")

    def _apply_asm_to_record(self, record: dict, host: dict, requested_ip: str) -> None:
        trail = host.get("discoveryTrail")
        self.add_field(record, "host_ip", _host_primary_ip(host, requested_ip))
        self.add_field(record, "domain", _domain_from_discovery_trail(trail))

    def _enrich_record_from_fetch(
        self, record: dict, requested_ip: str, headers: Dict[str, str]
    ) -> dict:
        host, failed = self._fetch_host_json(requested_ip, headers)
        if failed or not host:
            self._clear_enrichment_fields(record)
        else:
            self._apply_asm_to_record(record, host, requested_ip)
        return record

    def _flush_pending_batch(
        self,
        pending: List[Tuple[dict, str]],
        headers: Dict[str, str],
        batch_size: int,
    ) -> Iterator[dict]:
        """Run parallel fetches for pending (record, ip) pairs; yield records in order."""
        if not pending:
            return
        ips = [ip for _, ip in pending]
        workers = min(len(ips), batch_size or 1)
        with ThreadPoolExecutor(max_workers=workers) as pool:
            results = list(pool.map(lambda ip: self._fetch_host_json(ip, headers), ips))
        for (record, ip), (host, failed) in zip(pending, results):
            if failed or not host:
                self._clear_enrichment_fields(record)
            else:
                self._apply_asm_to_record(record, host, ip)
            yield record
        pending.clear()

    def _stream_without_pipeline(self, headers: Dict[str, str]) -> Iterator[dict]:
        # No upstream events: require ip=, split list, one GET per address, yield new rows.
        if _is_blank(self.ip):
            raise ValueError(
                "The ip option is required when no events are piped in "
                "(calls api/v1/assets/hosts/{ip})"
            )
        ips = [
            s.strip()
            for s in str(self.ip).split(",")
            if s and s.strip().lower() != "null"
        ]
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
        total_records = len(records)
        records_with_ip = 0
        for rec in records:
            rec_ip = rec.get(ip_field) or rec.get("ip")
            if not _is_blank(rec_ip):
                records_with_ip += 1

        total_batches = 0
        if batch_sz > 0 and records_with_ip > 0:
            total_batches = (records_with_ip + batch_sz - 1) // batch_sz

        _report_progress(
            "censysasmhosts",
            f"pipeline start: records={total_records}, batches={total_batches}",
        )

        batch_num = 0

        for record in records:
            ip = record.get(ip_field) or record.get("ip")
            if _is_blank(ip):
                self._clear_enrichment_fields(record)
                yield record
                continue

            if batch_sz > 0:
                pending.append((record, ip))
                if len(pending) >= batch_sz:
                    yield from self._flush_pending_batch(pending, headers, batch_sz)
                    batch_num += 1
                    _report_progress(
                        "censysasmhosts",
                        f"batch complete: {batch_num}/{total_batches}",
                    )
                    if delay_sec > 0:
                        time.sleep(delay_sec)
            else:
                yield self._enrich_record_from_fetch(record, ip, headers)

        n_final = len(pending)
        yield from self._flush_pending_batch(pending, headers, batch_sz)
        if n_final > 0:
            batch_num += 1
            _report_progress(
                "censysasmhosts",
                f"batch complete: {batch_num}/{total_batches}",
            )

    def stream(self, records):
        # Materialize input once so we can tell "no pipeline" vs "piped" by count.
        try:
            headers = self._request_headers()
        except Exception as e:
            _report_error("censysasmhosts", e)
            raise

        try:
            records_list = list(records)
        except Exception as e:
            _report_error("censysasmhosts", e)
            raise

        try:
            if not records_list:
                # Standalone: | censysasmhosts ip="..." — no events from the left.
                yield from self._stream_without_pipeline(headers)
            else:
                # Pipeline: | ... | censysasmhosts — enrich each incoming event.
                yield from self._stream_with_pipeline(records_list, headers)
        except Exception as e:
            _report_error("censysasmhosts", e)
            raise


dispatch(CensysAsmHostsCommand, sys.argv, sys.stdin, sys.stdout, __name__)
