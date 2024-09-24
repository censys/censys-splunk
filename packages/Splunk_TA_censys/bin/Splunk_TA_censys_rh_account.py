import splunk_ta_censys_declare

from splunk_aoblib.rest_migration import ConfigMigrationHandler
from splunktaucclib.rest_handler import admin_external, util
from splunktaucclib.rest_handler.endpoint import (
    RestModel,
    SingleModel,
    field,
    validator,
)
import requests


util.remove_http_proxy_env_vars()

def validate_api_key(value, *args, **kwargs):
    base_url = "https://app.censys.io/api"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Censys-Api-Key": value,
        "User-Agent": "Splunk_TA_censys",
    }
    try:
        resp = requests.get(f"{base_url}/integrations/v1/account", headers=headers)
    except requests.RequestException as e:
        raise validator.ValidationFailed("Failed to validate the API key")

fields = [
    field.RestField(
        "asm_api_key",
        required=True,
        encrypted=True,
        default=None,
        validator=validator.UserDefined(validate_api_key),
    ),
]
model = RestModel(fields, name=None)


endpoint = SingleModel(
    "splunk_ta_censys_account",
    model,
)


if __name__ == "__main__":
    admin_external.handle(
        endpoint,
        handler=ConfigMigrationHandler,
    )
