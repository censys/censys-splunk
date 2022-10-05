import json
import logging
import pathlib
from enum import Enum
from typing import Dict, Tuple

import censys_declare

from splunklib.client import StoragePasswords
from splunklib.searchcommands import GeneratingCommand

DEFAULT_APP_NAME = "censys"
DEFAULT_REALM = "censys_setup"
DEFAULT_SECRET_NAME = "censys_secrets"


class CensysSecretKeys(str, Enum):
    ASM_API_KEY = "censys_asm_api_key"
    SEARCH_APP_ID = "censys_search_app_id"
    SEARCH_APP_SECRET = "censys_search_app_secret"


class CensysGeneratingCommand(GeneratingCommand):
    def __init__(self):
        super().__init__()
        # TODO: Fix this path
        path = pathlib.Path(__file__).parent.parent
        log_path = path / "censys.log"
        if not log_path.exists():
            log_path.touch()
        handler = logging.FileHandler(str(log_path), mode="a")
        self.censys_logger = logging.getLogger("censys")
        self.censys_logger.addHandler(handler)
        self.censys_logger.setLevel(logging.INFO)

    def generate(self):
        pass

    def get_censys_secrets(self) -> Dict[str, str]:
        if self.service is None:
            raise ValueError(
                "This command must be run in a Splunk instance in order to retrieve Censys secrets"
            )
        storage_passwords: StoragePasswords = self.service.storage_passwords
        for password in storage_passwords:
            if (
                password.realm == DEFAULT_REALM
                and password.username == DEFAULT_SECRET_NAME
                and password.clear_password
            ):
                try:
                    return json.loads(password.clear_password)
                except json.JSONDecodeError:
                    # return password.clear_password
                    pass
        return {}

    def get_censys_asm_api_key(self) -> str:
        censys_secrets = self.get_censys_secrets()
        censys_asm_api_key = censys_secrets.get(CensysSecretKeys.ASM_API_KEY)
        if not censys_asm_api_key:
            raise ValueError("Censys ASM API key not found")
        return censys_asm_api_key

    def get_censys_search_api_credentials(self) -> Tuple[str, str]:
        censys_secrets = self.get_censys_secrets()
        censys_search_app_id = censys_secrets.get(CensysSecretKeys.SEARCH_APP_ID)
        censys_search_app_secret = censys_secrets.get(
            CensysSecretKeys.SEARCH_APP_SECRET
        )
        if not censys_search_app_id or not censys_search_app_secret:
            raise ValueError("Censys Search API credentials not found")
        return censys_search_app_id, censys_search_app_secret
