import json
import sys

import censys_declare

from censys_base_command import CensysGeneratingCommand
from splunklib.searchcommands import Configuration, dispatch

from censys.asm.risks import Risksv2

RISK_TYPES_SOURCETYPE = "censys:asm:risk-types"
RISK_TYPES_SOURCE = "censys_asm_risk_types"


@Configuration()
class CensysAsmRiskTypesCommand(CensysGeneratingCommand):
    """
    The censysasmrisktypes command generates a table of risk types.

    Example:

    ``| censysasmrisktypes``
    """

    def generate(self):
        asm_api_key = self.get_censys_asm_api_key()
        risks_client = Risksv2(asm_api_key)
        res = risks_client.get_risk_types(include_events=False)
        for risk_instance in res.get("types", []):
            yield {
                "_raw": json.dumps(risk_instance),
                "sourcetype": RISK_TYPES_SOURCETYPE,
                "source": RISK_TYPES_SOURCE,
                "output_mode": "json",
            }


dispatch(CensysAsmRiskTypesCommand, sys.argv, sys.stdin, sys.stdout, __name__)
