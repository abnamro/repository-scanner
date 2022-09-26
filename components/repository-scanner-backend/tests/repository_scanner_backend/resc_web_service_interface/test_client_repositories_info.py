# Standard Library
from unittest.mock import patch

# First Party
from repository_scanner_backend.resc_web_service.schema.repository_info import RepositoryInfoCreate
from repository_scanner_backend.resc_web_service_interface.repositories_info import create_repository_info


@patch("requests.post")
def test_create_repository_info(post):
    expected_url = 'https://fake-host.com/rws/v1/repositories-info'
    url = 'https://fake-host.com'

    repository_info = RepositoryInfoCreate(project_key="project_key",
                                           repository_id=1,
                                           repository_name="repository_name",
                                           repository_url="http://fake.repo.com",
                                           vcs_instance=1)
    expected_json = repository_info.json()

    _ = create_repository_info(url, repository_info)
    post.assert_called_once()
    post.assert_called_with(expected_url, data=expected_json, proxies={'http': '', 'https': ''})
