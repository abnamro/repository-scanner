# Standard Library
from datetime import datetime
from unittest.mock import patch

# First Party
from repository_scanner_backend.resc_web_service.schema.scan import ScanCreate
from repository_scanner_backend.resc_web_service_interface.scans import create_scan


@patch("requests.post")
def test_create_scan(post):
    expected_url = 'https://fake-host.com/rws/v1/scans'
    url = 'https://fake-host.com'

    scan = ScanCreate(scan_type="BASE", last_scanned_commit="FAKE_HASH", timestamp=datetime.utcnow(), branch_info_id=1,
                      rule_pack="1.2")
    expected_json = scan.json()

    _ = create_scan(url, scan)
    post.assert_called_once()
    post.assert_called_with(expected_url, data=expected_json, proxies={'http': '', 'https': ''})
