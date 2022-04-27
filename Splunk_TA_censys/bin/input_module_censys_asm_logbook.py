# encoding = utf-8

import json
from typing import Dict, Optional

import requests
from modinput_wrapper.base_modinput import BaseModInput
from splunklib.modularinput.event_writer import EventWriter
from splunklib.modularinput.validation_definition import ValidationDefinition

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

BASE_URL = "https://app.censys.io/api"


class CensysAsmInput:
    input_stanza: str
    base_url: str
    censys_asm_api_key: str
    headers: Dict[str, str]

    def __init__(
        self, helper: BaseModInput, event_writer: EventWriter, base_url: str = BASE_URL
    ):
        """Initialize the CensysAsmInput class."""
        self.helper = helper
        self.input_stanza: str = helper.get_input_stanza_names()

        self.event_writer = event_writer

        self.base_url = base_url
        self.censys_asm_api_key = helper.get_arg("censys_asm_api_key")
        if self.censys_asm_api_key is None:
            self.helper.log_error("Censys ASM API key is missing.")
            return

        self.headers = {
            "Content-Type": "application/json",
            "Censys-Api-Key": self.censys_asm_api_key,
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

    def get_logbook_cursor(self) -> Optional[str]:
        """Get the logbook cursor."""
        response = self._make_call("/v1/logbook-cursor", "POST")
        logbook_cursor = response.json().get("cursor")
        if logbook_cursor is None:
            self.helper.log_error("Failed to get logbook cursor.")
            self.helper.log_debug(response.text)
        return logbook_cursor
    
    def get_logbook_cursor_check_point(self, checkpoint_key_prefix: str = "asm_logbook_cursor_"):
        """Get the logbook cursor and set the check point."""
        checkpoint_key = checkpoint_key_prefix + self.input_stanza
        cursor_state = self.helper.get_check_point(checkpoint_key)
        if cursor_state is None:
            self.helper.log_debug("Getting new logbook cursor...")
            cursor_state = self.get_logbook_cursor()
            if cursor_state is not None:
                self.helper.set_check_point(checkpoint_key, cursor_state)
        return cursor_state

    def get_logbook_events(self, cursor: Optional[str] = None) -> dict:
        """Get the logbook events."""
        response = self._make_call("/v1/logbook", "GET", parameters={"cursor": cursor})
        return response.json()

    def pull_logbook_events(self):
        """Pull the logbook events."""
        cursor = self.get_logbook_cursor_check_point()

        self.helper.log_debug(f"Logbook cursor: {cursor}")
        self.helper.log_info(f"Pulling logbook events for input '{self.input_stanza}'...")

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

            logbook_events: list = res.get("events", [])
            self.helper.log_debug(f"Adding {len(logbook_events)} logbook events")

            end_of_events: bool = res.get("endOfEvents", False)
            for logbook_event in logbook_events:
                logbook_event["data_input_name"] = self.input_stanza
                event = self.helper.new_event(
                    data=json.dumps(logbook_event),
                    index=output_index,
                    source=input_type,
                    sourcetype=sourcetype,
                )
                self.event_writer.write_event(event)


def validate_input(helper: BaseModInput, definition: ValidationDefinition):
    """Validate the input stanza configurations."""
    censys_asm_api_key = definition.parameters.get("censys_asm_api_key", None)


def collect_events(helper: BaseModInput, ew: EventWriter):
    """Collect Censys ASM Logbook events."""
    asm_input = CensysAsmInput(helper, ew)
    asm_input.pull_logbook_events()
