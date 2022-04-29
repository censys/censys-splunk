# encoding = utf-8

from typing import Optional
import json

from modinput_wrapper.base_modinput import BaseModInput
from splunklib.modularinput.event_writer import EventWriter
from splunklib.modularinput.validation_definition import ValidationDefinition

from .censys_asm import CensysAsmApi, validate_api_key

"""
    IMPORTANT
    Edit only the validate_input and collect_events functions.
    Do not edit any other part in this file.
    This file is generated only once when creating the modular input.
"""
"""
# For advanced users, if you want to create single instance mod input, uncomment this method.
def use_single_instance_mode():
    return True
"""


class CensysAsmRisksApi(CensysAsmApi):
    input_stanza: str

    def __init__(self, helper: BaseModInput, base_url: str = ...):
        """Initialize the CensysAsmRisksApi class."""
        super().__init__(helper.get_arg("censys_asm_api_key"), helper, base_url)
        self.input_stanza: str = helper.get_input_stanza_names()

    def get_risks(
        self, page: int = 1, limit: int = 1000, computed_at: Optional[str] = None
    ) -> dict:
        """
        Get risks from Censys ASM
        """
        payload = {
            "limit": limit,
            "page": page,
            "sort": ["firstComputedAt", {"context.type": "asc"}],
        }
        if computed_at:
            payload["query"] = {
                "field": "firstComputedAt",
                "operator": "<",
                "value": computed_at,
            }
        response = self._make_call("/v2/risk-instances/search", "POST", payload=payload)
        return response.json()

    def get_risks_cursor_check_point(
        self, checkpoint_key_prefix: str = "asm_risks_cursor_"
    ):
        """Get the risks cursor and set the check point."""
        checkpoint_key = checkpoint_key_prefix + self.input_stanza
        cursor_state = self.helper.get_check_point(checkpoint_key)
        return cursor_state

    def write_risk_events(self, event_writer: EventWriter):
        """Write the risk events."""
        cursor = self.get_risks_cursor_check_point()

        output_index = self.helper.get_output_index()
        input_type = self.helper.get_input_type()
        sourcetype = self.helper.get_sourcetype()

        risks_response = self.get_risks(computed_at=cursor)

        for risk in risks_response.get("risks", []):
            risk["data_input_name"] = self.input_stanza
            event = self.helper.new_event(
                data=json.dumps(risk),
                index=output_index,
                source=input_type,
                sourcetype=sourcetype,
            )
            event_writer.write_event(event)


def validate_input(helper: BaseModInput, definition: ValidationDefinition):
    """Validate the input stanza configurations."""
    censys_asm_api_key = definition.parameters.get("censys_asm_api_key", None)
    validate_api_key(helper, censys_asm_api_key)


def collect_events(helper: BaseModInput, ew: EventWriter):
    """Collect Censys ASM Risk events."""
    risks_api = CensysAsmRisksApi(helper)
    risks_api.write_logbook_events(ew)
