import splunk_ta_censys_declare

import unittest
from typing import List, Optional
from unittest.mock import MagicMock

import pytest
from modinput_wrapper.base_modinput import BaseModInput
from pytest_mock import MockerFixture
from splunklib.modularinput.event_writer import EventWriter
from splunklib.modularinput.validation_definition import ValidationDefinition

BASE_URL = "https://app.censys.io/api"


class CensysTestCase(unittest.TestCase):
    mocker: MockerFixture

    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker: MockerFixture):
        """Injects fixtures into the test case.

        Args:
            mocker (MockerFixture): pytest-mock fixture.
        """
        # Inject mocker fixture
        self.mocker = mocker

    def mock_helper(self) -> MagicMock:
        """Mocks the helper."""
        return self.mocker.create_autospec(BaseModInput)

    def mock_event_writer(self) -> MagicMock:
        """Mocks the event writer."""
        return self.mocker.create_autospec(EventWriter)

    def mock_definition(self) -> MagicMock:
        """MOcks the definition."""
        return self.mocker.create_autospec(ValidationDefinition)
