# encoding = utf-8

import json
from typing import Optional

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

CHECKPOINT_KEY_PREFIX = "asm_logbook_cursor_"


class CensysAsmLogbookApi(CensysAsmApi):
    input_stanza: str

    def __init__(self, helper: BaseModInput):
        """Initialize the CensysAsmLogbookApi class."""
        censys_asm_api_key = helper.get_arg(
            "censys_asm_api_key"
        ) or helper.get_global_setting("censys_asm_api_key")
        super().__init__(censys_asm_api_key, helper)
        self.input_stanza: str = helper.get_input_stanza_names()

    def get_logbook_cursor(self) -> Optional[str]:
        """Get the logbook cursor."""
        response = self._make_call("/v1/logbook-cursor", "POST")
        logbook_cursor = response.json().get("cursor")
        if logbook_cursor is None:
            self.helper.log_error("Failed to get logbook cursor.")
            self.helper.log_debug(response.text)
        return logbook_cursor

    def update_logbook_cursor_check_point(
        self, cursor_state: str, checkpoint_key_prefix: str = CHECKPOINT_KEY_PREFIX
    ):
        """Update the logbook cursor check point."""
        checkpoint_key = checkpoint_key_prefix + self.input_stanza
        if cursor_state is not None:
            self.helper.log_debug(
                f"Setting check point: {checkpoint_key} to {cursor_state}"
            )
            self.helper.save_check_point(checkpoint_key, cursor_state)

    def get_logbook_cursor_check_point(
        self, checkpoint_key_prefix: str = CHECKPOINT_KEY_PREFIX
    ):
        """Get the logbook cursor and set the check point."""
        checkpoint_key = checkpoint_key_prefix + self.input_stanza
        cursor_state = self.helper.get_check_point(checkpoint_key)
        if cursor_state is None:
            self.helper.log_debug("Getting new logbook cursor...")
            cursor_state = self.get_logbook_cursor()
            if cursor_state is not None:
                self.helper.log_debug(
                    f"Setting check point: {checkpoint_key} to {cursor_state}"
                )
                self.helper.save_check_point(checkpoint_key, cursor_state)
        return cursor_state

    def get_logbook_events(self, cursor: Optional[str] = None) -> dict:
        """Get the logbook events."""
        response = self._make_call("/v1/logbook", "GET", parameters={"cursor": cursor})
        return response.json()

    def write_logbook_events(self, event_writer: EventWriter):
        """Write the logbook events."""
        cursor = self.get_logbook_cursor_check_point()

        self.helper.log_debug(f"Logbook cursor: {cursor}")
        self.helper.log_info(
            f"Pulling logbook events for input '{self.input_stanza}'..."
        )

        output_index = self.helper.get_output_index()
        input_type = self.helper.get_input_type()
        sourcetype = self.helper.get_sourcetype()

        end_of_events = False
        while not end_of_events:
            try:
                res = self.get_logbook_events(cursor)
            except requests.HTTPError as e:
                self.helper.log_error(str(e))
                break

            logbook_events: list[dict] = res.get("events", [])
            self.helper.log_debug(f"Adding {len(logbook_events)} logbook events...")

            end_of_events: bool = res.get("endOfEvents", False)
            for logbook_event in logbook_events:
                logbook_event["dataInputName"] = self.input_stanza
                event = self.helper.new_event(
                    data=json.dumps(logbook_event),
                    index=output_index,
                    source=input_type,
                    sourcetype=sourcetype,
                )
                event_writer.write_event(event)

            cursor = res.get("nextCursor")
            self.update_logbook_cursor_check_point(cursor)


def validate_input(helper: BaseModInput, definition: ValidationDefinition):
    """Validate the input stanza configurations."""
    censys_asm_api_key = definition.parameters.get("censys_asm_api_key", None)


def collect_events(helper: BaseModInput, ew: EventWriter):
    """Collect Censys ASM Logbook events."""
    logbook_api = CensysAsmLogbookApi(helper)
    logbook_api.write_logbook_events(ew)
