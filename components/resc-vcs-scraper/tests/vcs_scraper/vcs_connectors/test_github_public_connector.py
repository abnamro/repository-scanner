# Standard Library
import os
from unittest import mock

# Third Party
from github import Github

# First Party
from vcs_scraper.constants import GITHUB_PUBLIC
from vcs_scraper.model import Repository
from vcs_scraper.vcs_connectors.vcs_connector_factory import VCSConnectorFactory
from vcs_scraper.vcs_instances_parser import VCSInstance

from vcs_scraper.vcs_connectors.github_public_connector import GithubPublicConnector  # noqa: E402  # isort:skip

with mock.patch.dict(os.environ, {"VCS_INSTANCE_TOKEN": "token123", "VCS_INSTANCE_USERNAME": "user123"}):
    github_public_vcs_instance = VCSInstance(name="test_name1",
                                             provider_type=GITHUB_PUBLIC,
                                             hostname="fake.github.com",
                                             port=443,
                                             scheme="https",
                                             username="VCS_INSTANCE_USERNAME",
                                             token="VCS_INSTANCE_USERNAME",
                                             exceptions=[],
                                             scope=[])

AZURE_DEVOPS_HOST = "azure_devops-fake-host.com"
AZURE_DEVOPS_SCHEME = "https"
AZURE_DEVOPS_PORT = "443"
AZURE_DEVOPS_ACCESS_TOKEN = "FAKE_TOKEN"
AZURE_ORG = "no_company"

with mock.patch.dict(os.environ, {"VCS_INSTANCE_TOKEN": "token123", "VCS_INSTANCE_USERNAME": "user123"}):
    ado_vcs_instance = VCSInstance(name="test_name1",
                                   provider_type=GITHUB_PUBLIC,
                                   hostname="fake.github.com",
                                   port=443,
                                   scheme="https",
                                   username="VCS_INSTANCE_USERNAME",
                                   token="VCS_INSTANCE_TOKEN",
                                   exceptions=[],
                                   scope=[])


def test_export_repository_all_branches():
    repository_information = {
        'id': 1,
        'project_key': 'project1',
        'name': 'repo1',
        'html_url': "http://test.com/repo"
    }

    latest_commit = "abc123"

    vcs_instance_name = "test server"
    with mock.patch.dict(os.environ, {"SCAN_ONLY_MASTER_BRANCH": "false"}):
        result = GithubPublicConnector.export_repository(repository_information, latest_commit, vcs_instance_name)

    assert type(result) is Repository
    assert result.project_key == "project1"
    assert result.repository_id == "1"
    assert result.repository_name == "repo1"
    assert result.repository_url == "http://test.com/repo"
    assert result.vcs_instance_name == "test server"
    assert result.latest_commit == "abc123"


def test_create_github_client_from_vcs_instance():
    github_public_client: GithubPublicConnector = VCSConnectorFactory.create_client_from_vcs_instance(
        github_public_vcs_instance)
    assert isinstance(github_public_client, GithubPublicConnector)
    assert isinstance(github_public_client.api_client, Github)
