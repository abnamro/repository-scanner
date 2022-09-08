# Standard Library
from unittest.mock import patch

# First Party
from repository_scanner_backend.resc_web_service.schema.vcs_instance import VCSInstanceCreate
from repository_scanner_backend.resc_web_service_interface.vcs_instances import create_vcs_instance


@patch("requests.post")
def test_create_vcs_instance(post):
    expected_url = 'https://fake-host.com/sts/v1/vcs-instances'
    url = 'https://fake-host.com'

    vcs_instance = VCSInstanceCreate(name="bitbucket-dev", provider_type="BITBUCKET", hostname="dummy-host",
                                     port=8080,
                                     scheme="https", exceptions=[], scope=["Project1", "Project2"],
                                     organization="dummy_org")
    expected_json = vcs_instance.json()

    _ = create_vcs_instance(url, vcs_instance)
    post.assert_called_once()
    post.assert_called_with(expected_url, data=expected_json, proxies={'http': '', 'https': ''})
