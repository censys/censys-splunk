import datetime
import json
from typing import Optional

import pytest
from input_module_censys_asm_risks import CensysAsmRisksApi
from parameterized import parameterized

from tests.utils import CensysTestCase


class TestRiskInput(CensysTestCase):
    @pytest.mark.skip(reason="Not implemented")
    def test_validate_input(self):
        pass

    def test_update_risk_events_cursor_check_point(self):
        # Test data
        test_cursor = "test_cursor"
        test_checkpoint_key_pre = "asm_risk_events_cursor_"
        test_input_stanza = "stanza"
        test_checkpoint_key = test_checkpoint_key_pre + test_input_stanza

        # Mock
        mock_helper = self.mock_helper()
        mock_helper.get_input_stanza_names.return_value = test_input_stanza
        mock_save_checkpoint = mock_helper.save_check_point
        risk_api = CensysAsmRisksApi(mock_helper)

        # Actual call
        risk_api.update_risk_events_cursor_check_point(
            test_cursor, test_checkpoint_key_pre
        )

        # Assertions
        mock_save_checkpoint.assert_called_once_with(test_checkpoint_key, test_cursor)

    def test_get_risk_events_cursor_check_point(self):
        # Test data
        test_cursor = "test_cursor"
        test_checkpoint_key_pre = "asm_risk_events_cursor_"
        test_input_stanza = "stanza"
        test_checkpoint_key = test_checkpoint_key_pre + test_input_stanza

        # Mock
        mock_helper = self.mock_helper()
        mock_helper.get_input_stanza_names.return_value = test_input_stanza
        mock_get_checkpoint = mock_helper.get_check_point
        mock_get_checkpoint.return_value = test_cursor
        risk_api = CensysAsmRisksApi(mock_helper)

        # Actual call
        cursor = risk_api.get_risk_events_cursor_check_point(test_checkpoint_key_pre)

        # Assertions
        mock_get_checkpoint.assert_called_once_with(test_checkpoint_key)
        assert cursor == test_cursor

    @parameterized.expand(
        [
            (None, None, None),
            (None, None, 5),
            (None, 5, None),
            (None, 5, 5),
            ("test_cursor", None, None),
            ("test_cursor", 5, None),
            ("test_cursor", 5, 5),
            ("test_cursor", None, 5),
        ]
    )
    def test_get_risk_events(
        self, cursor: Optional[str], after_id: Optional[int], limit: Optional[int]
    ):
        # Test data
        test_risk_events = [{"id": 1}, {"id": 2}, {"id": 3}, {"id": 4}, {"id": 5}]
        start = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

        # Mock
        mock_helper = self.mock_helper()
        risk_api = CensysAsmRisksApi(mock_helper)
        mock_make_call = self.mocker.patch.object(risk_api, "_make_call")
        mock_make_call.return_value.json.return_value = test_risk_events

        # Actual call
        risk_events = risk_api.get_risk_events(start, cursor, after_id, limit)

        # Assertions
        mock_make_call.assert_called_once_with(
            "/v2/risk-events",
            "GET",
            parameters={
                "start": start,
                "cursor": cursor,
                "afterId": after_id,
                "limit": limit,
            },
        )
        assert risk_events == test_risk_events

    @parameterized.expand([("test_risk_type"), ("not_risk_type")])
    def test_get_risk_type(self, risk_type: str):
        # Test data
        test_risk_types: dict[str, dict] = {
            "test_risk_type": {"id": 1, "name": "Risk Type Display Name"}
        }

        # Mock
        mock_helper = self.mock_helper()
        risk_api = CensysAsmRisksApi(mock_helper)
        mock_make_call = self.mocker.patch.object(risk_api, "_make_call")
        mock_make_call.return_value.json.return_value = test_risk_types

        # Actual call
        risk_types = risk_api.get_risk_type(risk_type)

        # Assertions
        mock_make_call.assert_called_once_with(f"/v2/risk-types/{risk_type}", "GET")
        assert risk_types == test_risk_types

    def test_write_risk_events(self):
        # Test data
        start = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        test_next_cursor = "test_next_cursor"
        test_index = "test"
        test_input_type = "type"
        test_sourcetype = "censys:asm:risk"
        test_input_stanza = "stanza"
        test_risk_events = {
            "events": [
                {
                    "id": 1,
                    "riskType": "exposed-rsa-private-key",
                },
                {
                    "id": 2,
                    "riskType": "vulnerable-gitlab-cve-2021-22205",
                },
            ],
            "next": test_next_cursor,
            "endOfEvents": True,
            "total": 2,
        }
        test_risk_types = {
            "exposed-rsa-private-key": {
                "id": "exposed-rsa-private-key",
                "name": "Exposed RSA Private Key",
            },
            "vulnerable-gitlab-cve-2021-22205": {
                "id": "vulnerable-gitlab-cve-2021-22205",
                "name": "Vulnerable GitLab CVE-2021-22205",
            },
        }
        expected_calls = []
        for event in test_risk_events["events"]:
            event["dataInputName"] = test_input_stanza
            event["riskName"] = test_risk_types[event["riskType"]]["name"]
            event["operation"] = event.get("op")  # implementation adds this
            expected_calls.append(
                {
                    "data": json.dumps(event),
                    "sourcetype": test_sourcetype,
                    "source": test_input_type,
                    "index": test_index,
                }
            )

        # Mock
        mock_event_writer = self.mock_event_writer()
        mock_helper = self.mock_helper()

        mock_input_stanza = mock_helper.get_input_stanza_names
        mock_input_stanza.return_value = test_input_stanza

        mock_output_index = mock_helper.get_output_index
        mock_output_index.return_value = test_index

        mock_input_type = mock_helper.get_input_type
        mock_input_type.return_value = test_input_type

        mock_sourcetype = mock_helper.get_sourcetype
        mock_sourcetype.return_value = test_sourcetype

        mock_new_event = mock_helper.new_event

        risk_api = CensysAsmRisksApi(mock_helper)
        risk_api.risk_types = test_risk_types
        mock_cursor = self.mocker.patch.object(
            risk_api,
            "get_risk_events_cursor_check_point",
            return_value=test_next_cursor,
        )
        mock_get_risk_events = self.mocker.patch.object(
            risk_api, "get_risk_events", return_value=test_risk_events
        )
        mock_write_event = mock_event_writer.write_event
        mock_update_check_point = self.mocker.patch.object(
            risk_api, "update_risk_events_cursor_check_point"
        )

        # Actual call
        risk_api.write_risk_events(mock_event_writer)

        # Assertions
        mock_cursor.assert_called_once()
        mock_output_index.assert_called()
        mock_input_type.assert_called()
        mock_sourcetype.assert_called()
        for call_args in expected_calls:
            mock_new_event.assert_any_call(**call_args)
        assert mock_write_event.call_count == len(expected_calls)
        mock_update_check_point.assert_called_once_with(test_next_cursor)

    def test_collect_events(self):
        pass
