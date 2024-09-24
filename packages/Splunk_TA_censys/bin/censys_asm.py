# encoding = utf-8

from typing import Dict, Optional

import requests
from modinput_wrapper.base_modinput import BaseModInput

BASE_URL = "https://app.censys.io/api"


class CensysAsmApi:
    """
    Make a call to the Censys ASM API.
    """

    base_url: str
    censys_asm_api_key: str
    headers: Dict[str, str]
    helper: BaseModInput

    def __init__(
        self, censys_asm_api_key: str, helper: BaseModInput, base_url: str = BASE_URL
    ):
        """Initialize the CensysAsmApi class."""
        self.censys_asm_api_key = censys_asm_api_key
        if not self.censys_asm_api_key:
            helper.log_error("Censys ASM API key is missing.")
            return
        self.helper = helper
        self.base_url = base_url
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Censys-Api-Key": self.censys_asm_api_key,
            "User-Agent": "Splunk_TA_censys",
        }

    def _make_call(
        self,
        path: str,
        method: str,
        parameters: Optional[dict] = None,
        payload: Optional[dict] = None,
        **kwargs,
    ) -> requests.Response:
        """Make a call to the Censys ASM API."""
        kwargs = {"headers": self.headers, **kwargs}
        if parameters:
            kwargs["parameters"] = parameters
        if payload:
            kwargs["payload"] = payload
        return self.helper.send_http_request(self.base_url + path, method, **kwargs)

    def validate(self):
        """Validate the API key."""
        res = self._make_call(
            "/integrations/v1/account", "GET"
        )
        res.raise_for_status()

def validate_api_key(censys_asm_api_key: Optional[str]):
    """Validate the input.

    Args:
        censys_asm_api_key: The censys ASM API key.
        args: The arguments. (none used here)

    Raises:
        ValueError: If the API key is missing.
    """
    if not censys_asm_api_key:
        raise ValueError("Censys ASM API key is missing.")
    helper = BaseModInput()
    api = CensysAsmApi(censys_asm_api_key, helper)
    try:
        api.validate()
    except requests.HTTPError as e:
        raise ValueError(f"Invalid Censys ASM API key:
        {str(e)}") from e
