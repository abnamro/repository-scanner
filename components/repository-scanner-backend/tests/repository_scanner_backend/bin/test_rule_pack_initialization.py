# Standard Library
from unittest.mock import patch
from urllib import response

# Third Party
from requests import Session

# First Party
from repository_scanner_backend.bin.rule_pack_initialization import wait_for_api_to_up


@patch.object(Session, 'get')
def test_wait_for_api_to_up_is_successful(mock_get):
    response.status_code = 200
    mock_get.return_value = response
    result = wait_for_api_to_up(api_base_url="dummy-api-base-url")
    assert result is True


@patch.object(Session, 'get')
def test_wait_for_api_to_up_is_failed(mock_get):
    response.status_code = 404
    mock_get.return_value = response
    result = wait_for_api_to_up(api_base_url="dummy-api-base-url")
    assert result is False
