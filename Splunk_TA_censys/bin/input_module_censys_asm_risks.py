# encoding = utf-8

import os
import sys
import time
import datetime
from typing import Optional
import json

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


class CensysAsmRisksInput:
    def __init__(
        self, helper: BaseModInput, event_writer: EventWriter, base_url: str = BASE_URL
    ):
        self.helper = helper
        self.event_writer = event_writer
        self.base_url = base_url

        self.log_level = helper.get_log_level()

        self.opt_censys_asm_api_key = helper.get_arg("censys_asm_api_key")

        self.headers = {
            "Content-Type": "application/json",
            "Censys-Api-Key": self.opt_censys_asm_api_key,
        }

    def _make_call(
        self,
        path: str,
        method: str,
        parameters: Optional[dict] = None,
        payload: Optional[dict] = None,
        **kwargs,
    ) -> requests.Response:
        kwargs = {"headers": self.headers, **kwargs}
        if parameters:
            kwargs["parameters"] = parameters
        if payload:
            kwargs["payload"] = payload
        return self.helper.send_http_request(self.base_url + path, method, **kwargs)

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

    def pull_risks(self, checkpoint_key: str = "asm_risks_computed_at"):
        computed_at_state = self.helper.get_check_point(checkpoint_key)
        self.helper.log_debug(f"Risk computed at: {computed_at_state}")

        output_index = self.helper.get_output_index()
        input_type = self.helper.get_input_type()
        sourcetype = self.helper.get_sourcetype()

        risks_response = self.get_risks(computed_at=computed_at_state)

        for risk in risks_response.get("risks", []):
            event = self.helper.new_event(
                data=json.dumps(risk),
                index=output_index,
                source=input_type,
                sourcetype=sourcetype,
            )
            self.event_writer.write_event(event)


def validate_input(helper: BaseModInput, definition: ValidationDefinition):
    """Validate the input stanza configurations."""
    censys_asm_api_key = definition.parameters.get("censys_asm_api_key", None)


def collect_events(helper: BaseModInput, ew: EventWriter):
    """Collect Censys ASM Risk events."""
    risks_input = CensysAsmRisksInput(helper, ew)
    risks_input.pull_risks()
