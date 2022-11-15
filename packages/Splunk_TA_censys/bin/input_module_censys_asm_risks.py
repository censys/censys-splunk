# encoding = utf-8

import json
from typing import Dict, Optional

import requests
from modinput_wrapper.base_modinput import BaseModInput
from splunklib.modularinput.event_writer import EventWriter
from splunklib.modularinput.validation_definition import ValidationDefinition

from censys_asm import CensysAsmApi

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

CHECKPOINT_KEY_PREFIX = "asm_risks_cursor_"


class CensysAsmRisksApi(CensysAsmApi):
    input_stanza: str
    risk_types: Dict[str, dict]

    def __init__(self, helper: BaseModInput):
        """Initialize the CensysAsmLogbookApi class."""
        self.input_stanza: str = helper.get_input_stanza_names()
        opt_global_account = helper.get_arg("global_account", self.input_stanza)
        censys_asm_api_key = opt_global_account.get("asm_api_key")
        super().__init__(censys_asm_api_key, helper)
        self.risk_types = {}

    def update_risk_events_cursor_check_point(
        self, cursor_state: str, checkpoint_key_prefix: str = CHECKPOINT_KEY_PREFIX
    ):
        """Update the logbook cursor check point."""
        checkpoint_key = checkpoint_key_prefix + self.input_stanza
        if cursor_state is not None:
            self.helper.log_debug(
                f"Setting check point: {checkpoint_key} to {cursor_state}"
            )
            self.helper.save_check_point(checkpoint_key, cursor_state)

    def get_risk_events_cursor_check_point(
        self, checkpoint_key_prefix: str = CHECKPOINT_KEY_PREFIX
    ):
        """Get the risk events cursor and set the check point."""
        checkpoint_key = checkpoint_key_prefix + self.input_stanza
        cursor_state = self.helper.get_check_point(checkpoint_key)
        if cursor_state is None:
            self.helper.log_debug(
                f"Check point {checkpoint_key} is not set. Skipping..."
            )
        return cursor_state

    def get_risk_events(
        self,
        cursor: Optional[str] = None,
        after_id: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> dict:
        """Get the risk events."""
        response = self._make_call(
            "/v2/risk-events",
            "GET",
            parameters={"cursor": cursor, "afterId": after_id, "limit": limit},
        )
        return response.json()

    def get_risk_type(self, risk_type: str) -> dict:
        """Get the risk type."""
        if risk_type not in self.risk_types:
            response = self._make_call(f"/v2/risk-types/{risk_type}", "GET")
            self.risk_types[risk_type] = response.json()
        return self.risk_types[risk_type]

    def get_risk_type_name(self, risk_type: str) -> Optional[str]:
        """Get the risk type name."""
        risk_name = self.get_risk_type(risk_type).get("name")
        if risk_name is None:
            self.helper.log_error(f"Risk type {risk_type} not found.")
        return risk_name

    def write_risk_events(self, event_writer: EventWriter):
        """Write the risk events."""
        cursor = self.get_risk_events_cursor_check_point()

        self.helper.log_debug(f"Risk events cursor: {cursor}")
        self.helper.log_info(f"Pulling risk events for input '{self.input_stanza}'...")

        output_index = self.helper.get_output_index()
        input_type = self.helper.get_input_type()
        sourcetype = self.helper.get_sourcetype()

        end_of_events = False
        while not end_of_events:
            try:
                res = self.get_risk_events(cursor)
                end_of_events = res.get("endOfEvents", False)
            except requests.HTTPError as e:
                self.helper.log_error(str(e))
                break

            risk_events: list[dict] = res.get("events", [])
            total_events: int = res.get("total", 0)
            self.helper.log_debug(f"Adding {total_events} risk events...")

            for risk_event in risk_events:
                risk_event["dataInputName"] = self.input_stanza
                risk_type = risk_event.get("riskType")
                risk_event["riskName"] = self.get_risk_type_name(risk_type)
                event = self.helper.new_event(
                    data=json.dumps(risk_event),
                    index=output_index,
                    source=input_type,
                    sourcetype=sourcetype,
                )
                event_writer.write_event(event)

            cursor = res.get("next")
            self.update_risk_events_cursor_check_point(cursor)


def validate_input(helper: BaseModInput, definition: ValidationDefinition):
    """Validate the input stanza configurations."""
    global_account = definition.parameters.get("global_account", None)


def collect_events(helper, ew):
    """Implement your data collection logic here."""
    risks_api = CensysAsmRisksApi(helper)
    risks_api.write_risk_events(ew)
