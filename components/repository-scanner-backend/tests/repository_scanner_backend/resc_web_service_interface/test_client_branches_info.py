# Standard Library
from unittest.mock import patch

# First Party
from repository_scanner_backend.resc_web_service.schema.branch_info import BranchInfoCreate
from repository_scanner_backend.resc_web_service_interface.branches_info import create_branch_info


@patch("requests.post")
def test_create_branch_info(post):
    expected_url = 'https://fake-host.com/sts/v1/branches-info'
    url = 'https://fake-host.com'

    branch_info = BranchInfoCreate(branch_id=1,
                                   branch_name="branch_name",
                                   last_scanned_commit="last_scanned_commit",
                                   repository_info_id=2)
    expected_json = branch_info.json()

    _ = create_branch_info(url, branch_info)
    post.assert_called_once()
    post.assert_called_with(expected_url, data=expected_json, proxies={'http': '', 'https': ''})
