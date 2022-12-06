# Standard Library
from unittest.mock import patch

# First Party
from resc_backend.resc_web_service.schema.repository import RepositoryCreate
from resc_backend.resc_web_service_interface.repositories import create_repository


@patch("requests.post")
def test_create_repository(post):
    expected_url = 'https://fake-host.com/resc/v1/repositories'
    url = 'https://fake-host.com'

    repository = RepositoryCreate(project_key="project_key",
                                  repository_id=1,
                                  repository_name="repository_name",
                                  repository_url="http://fake.repo.com",
                                  vcs_instance=1)
    expected_json = repository.json()

    _ = create_repository(url, repository)
    post.assert_called_once()
    post.assert_called_with(expected_url, data=expected_json, proxies={'http': '', 'https': ''})
