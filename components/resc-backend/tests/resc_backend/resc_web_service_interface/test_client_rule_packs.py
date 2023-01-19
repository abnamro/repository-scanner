# Standard Library
from unittest.mock import patch

# First Party
from resc_backend.resc_web_service_interface.rule_packs import get_rule_packs


@patch("requests.get")
def test_get_rule_packs(get):
    expected_url = 'https://fake-host.com/resc/v1/rule-packs/versions'
    url = 'https://fake-host.com'
    expected_params = {"active": None, "skip": 0, "limit": 100}

    _ = get_rule_packs(url)
    get.assert_called_once()
    get.assert_called_with(expected_url, params=expected_params, proxies={'http': '', 'https': ''})


@patch("requests.get")
def test_get_rule_packs_when_version_provided(get):
    expected_url = 'https://fake-host.com/resc/v1/rule-packs/versions'
    url = 'https://fake-host.com'
    expected_params = {"version": "1.0.0", "active": None, "skip": 0, "limit": 100}

    _ = get_rule_packs(url=url, version="1.0.0")
    get.assert_called_once()
    get.assert_called_with(expected_url, params=expected_params, proxies={'http': '', 'https': ''})


@patch("requests.get")
def test_get_rule_packs_when_active_provided(get):
    expected_url = 'https://fake-host.com/resc/v1/rule-packs/versions'
    url = 'https://fake-host.com'
    expected_params = {"active": True, "skip": 0, "limit": 100}

    _ = get_rule_packs(url=url, active=True)
    get.assert_called_once()
    get.assert_called_with(expected_url, params=expected_params, proxies={'http': '', 'https': ''})


@patch("requests.get")
def test_get_rule_packs_when_version_and_active_provided(get):
    expected_url = 'https://fake-host.com/resc/v1/rule-packs/versions'
    url = 'https://fake-host.com'
    expected_params = {"version": "1.0.0", "active": False, "skip": 0, "limit": 100}

    _ = get_rule_packs(url=url, version="1.0.0", active=False)
    get.assert_called_once()
    get.assert_called_with(expected_url, params=expected_params, proxies={'http': '', 'https': ''})
