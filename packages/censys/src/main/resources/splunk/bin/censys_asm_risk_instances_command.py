import json
import sys

import censys_declare

from censys_base_command import CensysGeneratingCommand
from splunklib.searchcommands import Configuration, dispatch

from censys.asm.risks import Risksv2

RISK_INSTANCES_SOURCETYPE = "censys:asm:risk-instances"
RISK_INSTANCES_SOURCE = "censys_asm_risk_instances"


@Configuration()
class CensysAsmRiskInstancesCommand(CensysGeneratingCommand):
    """
    The censysasmriskinstances command generates a table of risk instances.

    Example:

    ``| censysasmriskinstances``
    """

    def generate(self):
        asm_api_key = self.get_censys_asm_api_key()
        risks_client = Risksv2(asm_api_key)
        res = risks_client.get_risk_instances(include_events=False)
        for risk_instance in res.get("risks", []):
            yield {
                "_raw": json.dumps(risk_instance),
                "sourcetype": RISK_INSTANCES_SOURCETYPE,
                "source": RISK_INSTANCES_SOURCE,
                "output_mode": "json",
            }


dispatch(CensysAsmRiskInstancesCommand, sys.argv, sys.stdin, sys.stdout, __name__)
