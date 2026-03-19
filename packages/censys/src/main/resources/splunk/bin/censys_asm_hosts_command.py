import json
import sys

import censys_declare

from censys_base_command import CensysGeneratingCommand
from splunklib.searchcommands import Configuration, dispatch, Option

from censys.asm.assets import HostsAssets

HOSTS_SOURCETYPE = "censys:asm:hosts"
HOSTS_SOURCE = "censys_asm_hosts"


@Configuration()
class CensysAsmHostsCommand(CensysGeneratingCommand):
    """
    The censysasmhosts command fetches host assets from ASM by IP.

    Example:

    ``| censysasmhosts ip="192.0.2.1"``
    ``| censysasmhosts ip="192.0.2.1,192.0.2.2,10.0.0.1"``
    """

    ip = Option(
        doc="IP address(es) of the host asset(s) to fetch (comma-separated; calls api/v1/assets/hosts/{ip} for each)"
    )

    def _is_empty_or_null(self, value):
        if value is None:
            return True
        s = str(value).strip()
        return not s or s.lower() == "null"

    def generate(self):
        if self._is_empty_or_null(self.ip):
            raise ValueError("The ip option is required")
        ips = [
            s.strip()
            for s in str(self.ip).split(",")
            if s is not None and s.strip() and s.strip().lower() != "null"
        ]
        if not ips:
            raise ValueError("The ip option must contain at least one IP address")
        asm_api_key = self.get_censys_asm_api_key()
        hosts_client = HostsAssets(asm_api_key)
        for ip in ips:
            if self._is_empty_or_null(ip):
                continue
            host = hosts_client.get_asset_by_id(ip)
            yield {
                "_raw": json.dumps(host),
                "sourcetype": HOSTS_SOURCETYPE,
                "source": HOSTS_SOURCE,
                "output_mode": "json",
            }


dispatch(CensysAsmHostsCommand, sys.argv, sys.stdin, sys.stdout, __name__)
