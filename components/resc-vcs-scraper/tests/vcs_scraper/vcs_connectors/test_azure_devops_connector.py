# Standard Library
import os
from unittest import mock

# Third Party
import requests

# First Party
from vcs_scraper.constants import AZURE_DEVOPS
from vcs_scraper.model import Repository
from vcs_scraper.vcs_connectors.vcs_connector_factory import VCSConnectorFactory
from vcs_scraper.vcs_instances_parser import VCSInstance

from vcs_scraper.vcs_connectors.azure_devops_connector import AzureDevopsConnector  # noqa: E402  # isort:skip

AZURE_DEVOPS_HOST = "azure_devops-fake-host.com"
AZURE_DEVOPS_SCHEME = "https"
AZURE_DEVOPS_PORT = "443"
AZURE_DEVOPS_ACCESS_TOKEN = "FAKE_TOKEN"
AZURE_ORG = "no_company"


with mock.patch.dict(os.environ, {"VCS_INSTANCE_TOKEN": "token123", "VCS_INSTANCE_USERNAME": "user123"}):
    ado_vcs_instance = VCSInstance(name="test_name1",
                                   provider_type=AZURE_DEVOPS,
                                   hostname="fake.ado.com",
                                   port=443,
                                   scheme="https",
                                   username="VCS_INSTANCE_USERNAME",
                                   token="VCS_INSTANCE_TOKEN",
                                   exceptions=[],
                                   scope=[])


def test_export_repository_all_branches():
    repository_information = {
        "project": {"name": "9999"},
        "name": "repo1",
        "id": "1234",
        "web_url": "http://test.com/repo.git"
    }

    branches_information = [{"name": "feature", "commit": {"commit_id": "ABCDEFG"}},
                            {"name": "master", "commit": {"commit_id": "QRSTUVWXYZ"}}]

    vcs_instance_name = "test server"
    with mock.patch.dict(os.environ, {"SCAN_ONLY_MASTER_BRANCH": "false"}):
        result = AzureDevopsConnector.export_repository(repository_information, branches_information,
                                                        vcs_instance_name)

    assert type(result) is Repository
    assert result.repository_name == "repo1"
    assert result.project_key == "9999"
    assert result.vcs_instance_name == "test server"
    assert len(result.branches) == 2
    assert result.branches[0].branch_id == "feature"
    assert result.branches[0].last_scanned_commit == "ABCDEFG"
    assert result.branches[1].branch_id == "master"
    assert result.branches[1].last_scanned_commit == "QRSTUVWXYZ"


def test_export_repository_main_branch_only():
    repository_information = {
        "project": {"name": "9999"},
        "name": "repo1",
        "id": "1234",
        "web_url": "http://test.com/repo.git"
    }

    branches_information = [{"name": "dontscanme1", "commit": {"commit_id": "ABCDEFGH"}},
                            {"name": "master", "commit": {"commit_id": "IJKLMNOP"}},
                            {"name": "dontscanme2", "commit": {"commit_id": "QRSTUVWXYZ"}}]

    vcs_instance_name = "test server"

    with mock.patch.dict(os.environ, {"SCAN_ONLY_MASTER_BRANCH": "true"}):
        result = AzureDevopsConnector.export_repository(repository_information, branches_information,
                                                        vcs_instance_name)

    assert type(result) is Repository
    assert result.repository_name == "repo1"
    assert result.project_key == "9999"
    assert result.vcs_instance_name == "test server"
    assert len(result.branches) == 1
    assert result.branches[0].branch_id == "master"
    assert result.branches[0].last_scanned_commit == "IJKLMNOP"


def test_export_repository_info_main_branch_only_upper_casing():
    repository_information = {
        "project": {"name": "9999"},
        "name": "repo1",
        "id": "1234",
        "web_url": "http://test.com/repo.git"
    }

    branches_information = [{"name": "MASTER", "commit": {"commit_id": "IJKLMNOP"}},
                            {"name": "dontscanme1", "commit": {"commit_id": "ABCDEFGH"}},
                            {"name": "dontscanme2", "commit": {"commit_id": "QRSTUVWXYZ"}}]

    vcs_instance_name = "test server"

    with mock.patch.dict(os.environ, {"SCAN_ONLY_MASTER_BRANCH": "true"}):
        result = AzureDevopsConnector.export_repository(repository_information, branches_information,
                                                        vcs_instance_name)

    assert type(result) is Repository
    assert result.repository_name == "repo1"
    assert result.project_key == "9999"
    assert result.vcs_instance_name == "test server"
    assert len(result.branches) == 1
    assert result.branches[0].branch_id == "MASTER"
    assert result.branches[0].last_scanned_commit == "IJKLMNOP"


def test_export_repository_main_branch_only_no_master():
    repository_information = {
        "project": {"name": "9999"},
        "name": "repo1",
        "id": "1234",
        "web_url": "http://test.com/repo.git"
    }

    branches_information = [{"name": "dontscanme1", "commit": {"commit_id": "ABCDEFGH"}},
                            {"name": "dontscanme2", "commit": {"commit_id": "QRSTUVWXYZ"}}]

    vcs_instance_name = "test server"

    with mock.patch.dict(os.environ, {"SCAN_ONLY_MASTER_BRANCH": "true"}):
        result = AzureDevopsConnector.export_repository(repository_information, branches_information,
                                                        vcs_instance_name)

    assert type(result) is Repository
    assert result.repository_name == "repo1"
    assert result.project_key == "9999"
    assert result.vcs_instance_name == "test server"
    assert len(result.branches) == 0


def test_export_repository_empty_branches():
    repository_information = {
        "project": {"name": "9999"},
        "name": "repo1",
        "id": "1234",
        "web_url": "http://test.com/repo.git"
    }

    branches_information = []

    vcs_instance_name = "test server"

    with mock.patch.dict(os.environ, {"SCAN_ONLY_MASTER_BRANCH": "true"}):
        result = AzureDevopsConnector.export_repository(repository_information, branches_information,
                                                        vcs_instance_name)

    assert type(result) is Repository
    assert result.repository_name == "repo1"
    assert result.project_key == "9999"
    assert result.vcs_instance_name == "test server"
    assert len(result.branches) == 0


def test_get_clone_url():
    urls = [{"href": "ssh://git@test.com/repo.git", "name": "ssh"},
            {"href": "http://test.com/repo.git", "name": "http"}]

    http_clone_url = AzureDevopsConnector.get_clone_url(urls, "http")
    ssh_clone_url = AzureDevopsConnector.get_clone_url(urls, "ssh")
    none_clone_url = AzureDevopsConnector.get_clone_url(urls, "none")

    assert http_clone_url == "http://test.com/repo.git"
    assert ssh_clone_url == "ssh://git@test.com/repo.git"
    assert none_clone_url == ""


def test_create_azure_devops_client_from_vcs_instance():

    azure_devops_client = VCSConnectorFactory.create_client_from_vcs_instance(ado_vcs_instance)
    session = requests.Session()
    session.headers['Authorization'] = f'Bearer {ado_vcs_instance.token}'
    assert azure_devops_client.url == f"{ado_vcs_instance.scheme}://{ado_vcs_instance.hostname}:" \
                                      f"{ado_vcs_instance.port}/{ado_vcs_instance.organization}"
    assert azure_devops_client.api_client.base_url == azure_devops_client.url
    assert azure_devops_client.api_client._config.credentials.password == ado_vcs_instance.token
