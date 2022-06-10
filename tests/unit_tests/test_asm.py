from typing import Optional

from parameterized import parameterized

from tests.utils import CensysTestCase

from censys_asm import CensysAsmApi

BASE_URL = "https://app.censys.io/api"


class TestCensysAsmApi(CensysTestCase):
    @parameterized.expand(
        [
            ("/test_path", "GET", {"key": "value"}, {"key": "value"}),
            ("/test_path", "GET"),
            ("/test_path", "GET", {"key": "value"}),
            ("/test_path", "GET", None, {"key": "value"}),
        ]
    )
    def test_make_call(
        self,
        path: str,
        method: str,
        parameters: Optional[dict] = None,
        payload: Optional[dict] = None,
    ):
        # Test data
        test_api_key = "test_api_key"
        test_headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Censys-Api-Key": test_api_key,
            "User-Agent": "Splunk_TA_censys",
        }

        # Mock
        mock_helper = self.mock_helper()
        mock_send_http_request = mock_helper.send_http_request

        # Actual call
        api = CensysAsmApi(test_api_key, mock_helper, BASE_URL)
        api._make_call(path, method, parameters, payload)

        # Assertions
        kwargs = {"headers": test_headers}
        if parameters is not None:
            kwargs["parameters"] = parameters
        if payload is not None:
            kwargs["payload"] = payload
        mock_send_http_request.assert_called_once_with(
            BASE_URL + path, method, **kwargs
        )

    def test_validate(self):
        # Test data
        test_api_key = "test_api_key"
        # Mock
        mock_helper = self.mock_helper()
        mock_api = CensysAsmApi(test_api_key, mock_helper, BASE_URL)

        mock_make_call = self.mocker.patch.object(mock_api, "_make_call")
        mock_response = self.mock_response()
        mock_raise_status = mock_response.return_value.raise_for_status
        mock_make_call.return_value = mock_response.return_value

        # Actual call
        mock_api.validate()

        # Assertions
        mock_make_call.assert_called_once_with(
            "/v1/assets/hosts", "GET", parameters={"pageSize": 1, "pageNumber": 1}
        )
        mock_raise_status.assert_called_once_with()
