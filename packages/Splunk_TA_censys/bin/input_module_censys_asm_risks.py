# encoding = utf-8

import datetime
import json
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional, Tuple

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
ENRICHMENT_MAX_WORKERS = 8


class CensysAsmRisksApi(CensysAsmApi):
    input_stanza: str
    risk_types: Dict[str, dict]

    def __init__(self, helper: BaseModInput):
        """Initialize the CensysAsmLogbookApi class."""
        self.helper = helper
        self.input_stanza: str = helper.get_input_stanza_names()
        opt_global_account = helper.get_arg("global_account", self.input_stanza)
        helper.log_debug(f"Global account: {opt_global_account}")
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
        start: Optional[str] = None,
        cursor: Optional[str] = None,
        after_id: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> dict:
        """Get the risk events."""
        response = self._make_call(
            "/v2/risk-events",
            "GET",
            parameters={
                "start": start,
                "cursor": cursor,
                "afterId": after_id,
                "limit": limit,
            },
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

    def get_risk_instance(self, risk_id: int) -> Optional[dict]:
        """Get the risk instance data by riskID from /v2/risk-instances/{id}."""
        try:
            self.helper.log_debug(f"Fetching risk instance: GET /v2/risk-instances/{risk_id}")
            response = self._make_call(f"/v2/risk-instances/{risk_id}", "GET")
            if not response.ok:
                self.helper.log_info(
                    f"Enrichment API failed for riskID={risk_id}: "
                    f"HTTP {response.status_code} {response.reason}"
                )
                return None
            return response.json()
        except requests.HTTPError as e:
            self.helper.log_error(
                f"Enrichment API failed for riskID={risk_id}: {e.__class__.__name__} {e}"
            )
            return None
        except json.JSONDecodeError as e:
            self.helper.log_error(
                f"Enrichment API failed for riskID={risk_id}: "
                f"invalid JSON in response ({e})"
            )
            return None

    def _apply_enrichment(
        self, risk_event: dict, risk_id: int, risk_instance: dict
    ) -> None:
        """Apply risk instance data (severity, ip, port, protocol) to a risk event."""
        severity = risk_instance.get("severity")
        if severity:
            risk_event["severity"] = severity
        context = risk_instance.get("context")
        if context:
            if context.get("ip") is not None:
                risk_event["ip"] = context["ip"]
            if context.get("port") is not None:
                risk_event["port"] = context["port"]
            if context.get("service") is not None:
                risk_event["protocol"] = context["service"]

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
                if cursor is not None:
                    res = self.get_risk_events(cursor=cursor)
                else:
                    # Get todays date and format it as 2022-04-04T00:00:00Z
                    today = datetime.datetime.now()
                    today = today.replace(hour=0, minute=0, second=0, microsecond=0)
                    todays_date = today.strftime("%Y-%m-%dT%H:%M:%SZ")
                    res = self.get_risk_events(start=todays_date)
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
                risk_event["operation"] = risk_event.get("op")

            # Collect (index, risk_id) for events that need enrichment
            to_enrich: List[Tuple[int, int]] = [
                (i, risk_events[i]["riskID"])
                for i in range(len(risk_events))
                if risk_events[i].get("riskID") is not None
            ]

            # Fetch risk instances in parallel (dedupe risk_ids to avoid redundant API calls)
            risk_id_to_instance: Dict[int, Optional[dict]] = {}
            if to_enrich:
                unique_risk_ids = list(
                    dict.fromkeys(rid for _, rid in to_enrich)
                )
                with ThreadPoolExecutor(max_workers=ENRICHMENT_MAX_WORKERS) as executor:
                    instances = list(
                        executor.map(self.get_risk_instance, unique_risk_ids)
                    )
                risk_id_to_instance = dict(zip(unique_risk_ids, instances))

            # Apply enrichment and write events
            for i, risk_event in enumerate(risk_events):
                risk_id = risk_event.get("riskID")
                if risk_id is not None:
                    risk_instance = risk_id_to_instance.get(risk_id)
                    if risk_instance:
                        self._apply_enrichment(risk_event, risk_id, risk_instance)
                        self.helper.log_info(
                            f"Enrichment applied for riskID={risk_id} "
                            f"(event id={risk_event.get('id')})"
                        )
                    else:
                        self.helper.log_info(
                            f"Enrichment failed for riskID={risk_id}: risk instance API returned no data"
                        )
                else:
                    self.helper.log_debug(
                        f"Event id={risk_event.get('id')} has no riskID, skipping enrichment"
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
    global_account = definition.parameters.get("global_account", None)


def collect_events(helper, ew):
    """Implement your data collection logic here."""
    risks_api = CensysAsmRisksApi(helper)
    risks_api.write_risk_events(ew)
