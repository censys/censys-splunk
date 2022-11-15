import splunk_ta_censys_declare

from splunk_aoblib.rest_migration import ConfigMigrationHandler
from splunktaucclib.rest_handler import admin_external, util
from splunktaucclib.rest_handler.endpoint import (
    RestModel,
    SingleModel,
    field,
    validator,
)

util.remove_http_proxy_env_vars()


fields = [
    field.RestField(
        "asm_api_key",
        required=False,
        encrypted=False,
        default=None,
        validator=validator.String(
            min_len=36,
            max_len=36,
        ),
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
