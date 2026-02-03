import datetime
import json
from typing import Optional

import pytest
from input_module_censys_asm_logbook import CensysAsmLogbookApi, collect_events
from parameterized import parameterized

from tests.utils import CensysTestCase


class TestLogbookInput(CensysTestCase):
    @pytest.mark.skip(reason="Not implemented")
    def test_validate_input(self):
        pass

    def test_collect_events(self):
        # Mock
        mock_helper = self.mock_helper()
        mock_event_writer = self.mock_event_writer()
        mock_logbook_api = self.mocker.patch(
            "input_module_censys_asm_logbook.CensysAsmLogbookApi"
        )
        mock_logbook_api.return_value = self.mocker.MagicMock()
        mock_write_logbook_events = mock_logbook_api.return_value.write_logbook_events

        # Actual call
        collect_events(mock_helper, mock_event_writer)

        # Assertions
        mock_logbook_api.assert_called_once_with(mock_helper)
        mock_write_logbook_events.assert_called_once_with(mock_event_writer)

    def test_get_logbook_cursor(self):
        # Test data
        test_cursor = "test_cursor"
        today = datetime.datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        todays_date = today.strftime("%Y-%m-%dT%H:%M:%SZ")

        # Mock
        mock_helper = self.mock_helper()
        logbook_api = CensysAsmLogbookApi(mock_helper)
        mock_make_call = self.mocker.patch.object(logbook_api, "_make_call")
        mock_make_call.return_value.json.return_value = {"cursor": test_cursor}

        # Actual call
        cursor = logbook_api.get_logbook_cursor()

        # Assertions (implementation uses payload= for POST body, not parameters=)
        mock_make_call.assert_called_once_with(
            "/v1/logbook-cursor",
            "POST",
            payload={"dateFrom": todays_date},
        )
        assert cursor == test_cursor

    def test_update_logbook_cursor_check_point(self):
        # Test data
        test_cursor = "test_cursor"
        test_checkpoint_key_pre = "asm_logbook_cursor_"
        test_input_stanza = "stanza"
        test_checkpoint_key = test_checkpoint_key_pre + test_input_stanza

        # Mock
        mock_helper = self.mock_helper()
        mock_helper.get_input_stanza_names.return_value = test_input_stanza
        mock_save_checkpoint = mock_helper.save_check_point
        logbook_api = CensysAsmLogbookApi(mock_helper)

        # Actual call
        logbook_api.update_logbook_cursor_check_point(
            test_cursor, test_checkpoint_key_pre
        )

        # Assertions
        mock_save_checkpoint.assert_called_once_with(test_checkpoint_key, test_cursor)

    @parameterized.expand([(True, None), (False, True), (False, False)])
    def test_get_logbook_cursor_check_point(
        self, has_checkpoint: bool, fetch_checkpoint: Optional[bool] = None
    ):
        # Test data
        test_cursor = "test_cursor"
        test_checkpoint_key_pre = "asm_logbook_cursor_"
        test_input_stanza = "stanza"
        test_checkpoint_key = test_checkpoint_key_pre + test_input_stanza

        # Mock
        mock_helper = self.mock_helper()
        mock_helper.get_input_stanza_names.return_value = test_input_stanza
        mock_get_checkpoint = mock_helper.get_check_point
        mock_get_checkpoint.return_value = test_cursor if has_checkpoint else None
        mock_save_checkpoint = mock_helper.save_check_point
        logbook_api = CensysAsmLogbookApi(mock_helper)
        mock_get_cursor = self.mocker.patch.object(logbook_api, "get_logbook_cursor")
        mock_get_cursor.return_value = (
            test_cursor if fetch_checkpoint else fetch_checkpoint
        )

        # Actual call
        cursor_state = logbook_api.get_logbook_cursor_check_point(
            test_checkpoint_key_pre
        )

        # Assertions
        if has_checkpoint:
            mock_get_checkpoint.assert_called_once_with(test_checkpoint_key)
            assert cursor_state == test_cursor

        # Got checkpoint, but not fetching
        if fetch_checkpoint is None:
            mock_save_checkpoint.assert_not_called()
        # Did not get checkpoint and fetching
        elif fetch_checkpoint:
            mock_get_cursor.assert_called_once()
            mock_save_checkpoint.assert_called_once_with(
                test_checkpoint_key, test_cursor
            )
        # Did not get checkpoint and fetch error
        else:
            assert cursor_state == False

    @parameterized.expand([(None,), ("test_cursor",)])
    def test_get_logbook_events(self, cursor: Optional[str]):
        # Test data
        test_res = {"events": []}

        # Mock
        mock_helper = self.mock_helper()
        logbook_api = CensysAsmLogbookApi(mock_helper)
        mock_make_call = self.mocker.patch.object(logbook_api, "_make_call")
        mock_make_call.return_value.json.return_value = test_res

        # Actual call
        res = logbook_api.get_logbook_events(cursor)

        # Assertions
        mock_make_call.assert_called_once_with(
            "/v1/logbook", "GET", parameters={"cursor": cursor}
        )
        assert res == test_res

    def test_write_logbook_events(self):
        # Test data
        test_cursor = "test_cursor"
        test_next_cursor = "test_next_cursor"
        test_index = "test"
        test_input_type = "type"
        test_sourcetype = "censys:asm:logbook"
        test_input_stanza = "stanza"
        test_logbook_events = {
            "events": [{"id": 1}, {"id": 2}],
            "endOfEvents": True,
            "nextCursor": test_next_cursor,
        }
        expected_calls = []
        for event in test_logbook_events["events"]:
            event["dataInputName"] = test_input_stanza
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
        mock_helper.get_input_stanza_names.return_value = test_input_stanza
        mock_output_index = mock_helper.get_output_index
        mock_output_index.return_value = test_index
        mock_input_type = mock_helper.get_input_type
        mock_input_type.return_value = test_input_type
        mock_sourcetype = mock_helper.get_sourcetype
        mock_sourcetype.return_value = test_sourcetype
        mock_new_event = mock_helper.new_event
        logbook_api = CensysAsmLogbookApi(mock_helper)
        mock_cursor = self.mocker.patch.object(
            logbook_api, "get_logbook_cursor_check_point", return_value=test_cursor
        )
        mock_get_logbook_events = self.mocker.patch.object(
            logbook_api, "get_logbook_events", return_value=test_logbook_events
        )
        mock_write_event = mock_event_writer.write_event
        mock_update_check_point = self.mocker.patch.object(
            logbook_api, "update_logbook_cursor_check_point"
        )

        # Actual call
        logbook_api.write_logbook_events(mock_event_writer)

        # Assertions
        mock_cursor.assert_called_once()
        mock_get_logbook_events.assert_called_with(test_cursor)
        mock_output_index.assert_called()
        mock_input_type.assert_called()
        mock_sourcetype.assert_called()
        for call_args in expected_calls:
            mock_new_event.assert_any_call(**call_args)
        assert mock_write_event.call_count == len(expected_calls)
        mock_update_check_point.assert_called_once_with(test_next_cursor)
