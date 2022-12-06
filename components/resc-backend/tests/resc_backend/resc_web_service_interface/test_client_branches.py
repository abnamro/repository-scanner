# Standard Library
from unittest.mock import patch

# First Party
from resc_backend.resc_web_service.schema.branch import BranchCreate
from resc_backend.resc_web_service_interface.branches import create_branch


@patch("requests.post")
def test_create_branch(post):
    expected_url = 'https://fake-host.com/resc/v1/branches'
    url = 'https://fake-host.com'

    branch = BranchCreate(branch_id=1,
                          branch_name="branch_name",
                          latest_commit="latest_commit",
                          repository_id=2)
    expected_json = branch.json()

    _ = create_branch(url, branch)
    post.assert_called_once()
    post.assert_called_with(expected_url, data=expected_json, proxies={'http': '', 'https': ''})
