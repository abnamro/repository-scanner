# Standard Library
import os
from unittest import mock

# Third Party
import requests

# First Party
from vcs_scraper.constants import BITBUCKET
from vcs_scraper.model import RepositoryInfo
from vcs_scraper.vcs_connectors.vcs_connector_factory import VCSConnectorFactory
from vcs_scraper.vcs_instances_parser import VCSInstance

from vcs_scraper.vcs_connectors.bitbucket_connector import BitbucketConnector  # noqa: E402  # isort:skip

with mock.patch.dict(os.environ, {"VCS_INSTANCE_TOKEN": "token123", "VCS_INSTANCE_USERNAME": "user123"}):
    btbk_vcs_instance = VCSInstance(name="test_name2",
                                    provider_type=BITBUCKET,
                                    hostname="fake.bitbucket.com",
                                    port=443,
                                    scheme="https",
                                    username="VCS_INSTANCE_USERNAME",
                                    token="VCS_INSTANCE_TOKEN",
                                    exceptions=[],
                                    scope=[])


def test_export_repository_info_all_branches():
    repository_information = {
        "project": {"key": "9999"},
        "name": "repo1",
        "id": "1234",
        "links": {"clone": [{"href": "ssh://git@test.com/repo.git", "name": "ssh"},
                            {"href": "http://test.com/repo.git", "name": "http"}], "self": "bla"}
    }

    branches_information = [{"id": "features/1", "displayId": "1", "latestCommit": "ABCDEFG"},
                            {"id": "/refs/heads/main", "displayId": "main", "latestCommit": "QRSTUVWXYZ"}]

    vcs_instance_name = "test server"

    with mock.patch.dict(os.environ, {"SCAN_ONLY_MASTER_BRANCH": "false"}):
        result = BitbucketConnector.export_repository_info(repository_information, branches_information,
                                                           vcs_instance_name)

    assert type(result) is RepositoryInfo
    assert result.repository_name == "repo1"
    assert result.project_key == "9999"
    assert result.vcs_instance_name == "test server"
    assert len(result.branches_info) == 2
    assert result.branches_info[0].branch_id == "features/1"
    assert result.branches_info[0].last_scanned_commit == "ABCDEFG"
    assert result.branches_info[1].branch_id == "/refs/heads/main"
    assert result.branches_info[1].last_scanned_commit == "QRSTUVWXYZ"


def test_export_repository_info_main_branch_only():
    repository_information = {
        "project": {"key": "9999"},
        "name": "repo1",
        "id": "1234",
        "links": {"clone": [{"href": "ssh://git@test.com/repo.git", "name": "ssh"},
                            {"href": "http://test.com/repo.git", "name": "http"}], "self": "bla"}
    }

    branches_information = [{"id": "/refs/heads/dontscanme1", "displayId": "dontscanme1", "latestCommit": "ABCDEFGH"},
                            {"id": "/refs/heads/main", "displayId": "main", "latestCommit": "IJKLMNOP"},
                            {"id": "/refs/heads/dontscanme2", "displayId": "dontscanme2", "latestCommit": "QRSTUVWXYZ"}]

    vcs_instance_name = "test server"

    with mock.patch.dict(os.environ, {"SCAN_ONLY_MASTER_BRANCH": "true"}):
        result = BitbucketConnector.export_repository_info(repository_information, branches_information,
                                                           vcs_instance_name)

    assert type(result) is RepositoryInfo
    assert result.repository_name == "repo1"
    assert result.project_key == "9999"
    assert result.vcs_instance_name == "test server"
    assert len(result.branches_info) == 1
    assert result.branches_info[0].branch_id == "/refs/heads/main"
    assert result.branches_info[0].last_scanned_commit == "IJKLMNOP"


def test_export_repository_info_main_branch_only_upper_casing():
    repository_information = {
        "project": {"key": "9999"},
        "name": "repo1",
        "id": "1234",
        "links": {"clone": [{"href": "ssh://git@test.com/repo.git", "name": "ssh"},
                            {"href": "http://test.com/repo.git", "name": "http"}], "self": "bla"}
    }

    branches_information = [{"id": "/refs/heads/MAIN", "displayId": "MAIN", "latestCommit": "IJKLMNOP"},
                            {"id": "/refs/heads/dontscanme1", "displayId": "dontscanme1", "latestCommit": "ABCDEFGH"},
                            {"id": "/refs/heads/dontscanme2", "displayId": "dontscanme2", "latestCommit": "QRSTUVWXYZ"}]

    vcs_instance_name = "test server"

    with mock.patch.dict(os.environ, {"SCAN_ONLY_MASTER_BRANCH": "true"}):
        result = BitbucketConnector.export_repository_info(repository_information, branches_information,
                                                           vcs_instance_name)

    assert type(result) is RepositoryInfo
    assert result.repository_name == "repo1"
    assert result.project_key == "9999"
    assert result.vcs_instance_name == "test server"
    assert len(result.branches_info) == 1
    assert result.branches_info[0].branch_id == "/refs/heads/MAIN"
    assert result.branches_info[0].last_scanned_commit == "IJKLMNOP"


def test_export_repository_info_main_branch_only_no_master():
    repository_information = {
        "project": {"key": "9999"},
        "name": "repo1",
        "id": "1234",
        "links": {"clone": [{"href": "ssh://git@test.com/repo.git", "name": "ssh"},
                            {"href": "http://test.com/repo.git", "name": "http"}], "self": "bla"}
    }

    branches_information = [{"id": "/refs/heads/dontscanme1", "displayId": "dontscanme1", "latestCommit": "ABCDEFGH"},
                            {"id": "/refs/heads/dontscanme2", "displayId": "dontscanme2", "latestCommit": "QRSTUVWXYZ"}]

    vcs_instance_name = "test server"

    with mock.patch.dict(os.environ, {"SCAN_ONLY_MASTER_BRANCH": "true"}):
        result = BitbucketConnector.export_repository_info(repository_information, branches_information,
                                                           vcs_instance_name)

    assert type(result) is RepositoryInfo
    assert result.repository_name == "repo1"
    assert result.project_key == "9999"
    assert result.vcs_instance_name == "test server"
    assert len(result.branches_info) == 0


def test_export_repository_info_empty_branches():
    repository_information = {
        "project": {"key": "9999"},
        "name": "repo1",
        "id": "1234",
        "links": {"clone": [{"href": "ssh://git@test.com/repo.git", "name": "ssh"},
                            {"href": "http://test.com/repo.git", "name": "http"}], "self": "bla"}
    }

    branches_information = []

    vcs_instance_name = "test server"

    with mock.patch.dict(os.environ, {"SCAN_ONLY_MASTER_BRANCH": "true"}):
        result = BitbucketConnector.export_repository_info(repository_information, branches_information,
                                                           vcs_instance_name)

    assert type(result) is RepositoryInfo
    assert result.repository_name == "repo1"
    assert result.project_key == "9999"
    assert result.vcs_instance_name == "test server"
    assert len(result.branches_info) == 0


def test_get_clone_url():
    urls = [{"href": "ssh://git@test.com/repo.git", "name": "ssh"},
            {"href": "http://test.com/repo.git", "name": "http"}]

    http_clone_url = BitbucketConnector.get_clone_url(urls, "http")
    ssh_clone_url = BitbucketConnector.get_clone_url(urls, "ssh")
    none_clone_url = BitbucketConnector.get_clone_url(urls, "none")

    assert http_clone_url == "http://test.com/repo.git"
    assert ssh_clone_url == "ssh://git@test.com/repo.git"
    assert none_clone_url == ""


def test_create_bitbucket_client_from_vcs_instance():

    bitbucket_client = VCSConnectorFactory.create_client_from_vcs_instance(btbk_vcs_instance)
    session = requests.Session()
    session.headers['Authorization'] = f'Bearer {btbk_vcs_instance.token}'
    assert bitbucket_client.url == f"{btbk_vcs_instance.scheme}://{btbk_vcs_instance.hostname}" \
                                   f":{btbk_vcs_instance.port}"
    assert bitbucket_client.api_client.url == bitbucket_client.url
    assert bitbucket_client.api_client._session.headers['Authorization'] == session.headers['Authorization']
