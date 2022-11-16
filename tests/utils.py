import unittest
from typing import Any
from unittest.mock import MagicMock

import splunk_ta_censys_declare

import pytest
from modinput_wrapper.base_modinput import BaseModInput
from pytest_mock import MockerFixture
from requests import Response
from splunklib.modularinput.event_writer import EventWriter
from splunklib.modularinput.validation_definition import ValidationDefinition

BASE_URL = "https://app.censys.io/api"


class CensysTestCase(unittest.TestCase):
    mocker: MockerFixture
    freezer: Any

    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker: MockerFixture, freezer):
        """Injects fixtures into the test case.

        Args:
            mocker (MockerFixture): pytest-mock fixture.
        """
        # Inject mocker fixture
        self.mocker = mocker
        # Inject freezer fixture
        self.freezer = freezer
        self.freezer.move_to("2022-01-01 00:00:00")

    def mock_helper(self) -> MagicMock:
        """Mocks the helper."""
        return self.mocker.create_autospec(BaseModInput)

    def mock_event_writer(self) -> MagicMock:
        """Mocks the event writer."""
        return self.mocker.create_autospec(EventWriter)

    def mock_definition(self) -> MagicMock:
        """Mocks the definition."""
        return self.mocker.create_autospec(ValidationDefinition)

    def mock_response(self) -> MagicMock:
        """Mocks the response."""
        return self.mocker.create_autospec(Response)
