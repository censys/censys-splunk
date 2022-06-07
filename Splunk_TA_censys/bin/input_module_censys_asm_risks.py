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
        censys_asm_api_key = helper.get_arg(
            "censys_asm_api_key"
        ) or helper.get_global_setting("censys_asm_api_key")
        super().__init__(censys_asm_api_key, helper)
        self.input_stanza: str = helper.get_input_stanza_names()
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
            except requests.HTTPError as e:
                self.helper.log_error(str(e))
                break

            risk_events: list[dict] = res.get("events", [])
            total_events: int = res.get("total", 0)
            self.helper.log_debug(f"Adding {total_events} risk events...")

            for risk_event in risk_events:
                risk_event["data_input_name"] = self.input_stanza
                risk_event["riskName"] = self.get_risk_type(risk_event["riskType"]).get(
                    "displayName"
                )
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
    censys_asm_api_key = definition.parameters.get("censys_asm_api_key", None)


def collect_events(helper, ew):
    """Implement your data collection logic here

    # The following examples get the arguments of this input.
    # Note, for single instance mod input, args will be returned as a dict.
    # For multi instance mod input, args will be returned as a single value.
    opt_censys_asm_api_key = helper.get_arg('censys_asm_api_key')
    # In single instance mode, to get arguments of a particular input, use
    opt_censys_asm_api_key = helper.get_arg('censys_asm_api_key', stanza_name)

    # get input type
    helper.get_input_type()

    # The following examples get input stanzas.
    # get all detailed input stanzas
    helper.get_input_stanza()
    # get specific input stanza with stanza name
    helper.get_input_stanza(stanza_name)
    # get all stanza names
    helper.get_input_stanza_names()

    # The following examples get options from setup page configuration.
    # get the loglevel from the setup page
    loglevel = helper.get_log_level()
    # get proxy setting configuration
    proxy_settings = helper.get_proxy()
    # get account credentials as dictionary
    account = helper.get_user_credential_by_username("username")
    account = helper.get_user_credential_by_id("account id")
    # get global variable configuration
    global_censys_asm_api_key = helper.get_global_setting("censys_asm_api_key")

    # The following examples show usage of logging related helper functions.
    # write to the log for this modular input using configured global log level or INFO as default
    helper.log("log message")
    # write to the log using specified log level
    helper.log_debug("log message")
    helper.log_info("log message")
    helper.log_warning("log message")
    helper.log_error("log message")
    helper.log_critical("log message")
    # set the log level for this modular input
    # (log_level can be "debug", "info", "warning", "error" or "critical", case insensitive)
    helper.set_log_level(log_level)

    # The following examples send rest requests to some endpoint.
    response = helper.send_http_request(url, method, parameters=None, payload=None,
                                        headers=None, cookies=None, verify=True, cert=None,
                                        timeout=None, use_proxy=True)
    # get the response headers
    r_headers = response.headers
    # get the response body as text
    r_text = response.text
    # get response body as json. If the body text is not a json string, raise a ValueError
    r_json = response.json()
    # get response cookies
    r_cookies = response.cookies
    # get redirect history
    historical_responses = response.history
    # get response status code
    r_status = response.status_code
    # check the response status, if the status is not successful, raise requests.HTTPError
    response.raise_for_status()

    # The following examples show usage of check pointing related helper functions.
    # save checkpoint
    helper.save_check_point(key, state)
    # delete checkpoint
    helper.delete_check_point(key)
    # get checkpoint
    state = helper.get_check_point(key)

    # To create a splunk event
    helper.new_event(data, time=None, host=None, index=None, source=None, sourcetype=None, done=True, unbroken=True)
    """

    """
    # The following example writes a random number as an event. (Multi Instance Mode)
    # Use this code template by default.
    import random
    data = str(random.randint(0,100))
    event = helper.new_event(source=helper.get_input_type(), index=helper.get_output_index(), sourcetype=helper.get_sourcetype(), data=data)
    ew.write_event(event)
    """

    """
    # The following example writes a random number as an event for each input config. (Single Instance Mode)
    # For advanced users, if you want to create single instance mod input, please use this code template.
    # Also, you need to uncomment use_single_instance_mode() above.
    import random
    input_type = helper.get_input_type()
    for stanza_name in helper.get_input_stanza_names():
        data = str(random.randint(0,100))
        event = helper.new_event(source=input_type, index=helper.get_output_index(stanza_name), sourcetype=helper.get_sourcetype(stanza_name), data=data)
        ew.write_event(event)
    """
    risks_api = CensysAsmRisksApi(helper)
    risks_api.write_risk_events(ew)
