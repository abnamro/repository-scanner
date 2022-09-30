# Standard Library
import os
from unittest import mock
from unittest.mock import patch

# Third Party
from celery import Celery

# First Party
from vcs_scraper.constants import AZURE_DEVOPS, BITBUCKET, REPOSITORY_QUEUE
from vcs_scraper.model import BranchInfo, RepositoryInfo
from vcs_scraper.vcs_connectors.vcs_connector_factory import VCSConnectorFactory
from vcs_scraper.vcs_instances_parser import VCSInstance

RESC_RABBITMQ_SERVICE_HOST = "fake-rabbitmq-host.com"
RABBITMQ_DEFAULT_VHOST = "vhost"
RABBITMQ_USERNAME = "fake_rabbituser"
RABBITMQ_PASSWORD = "fake_password"
VCS_INSTANCES_FILE_PATH = "fake_path.json"

with mock.patch.dict(os.environ, {
                                  "RESC_RABBITMQ_SERVICE_HOST": RESC_RABBITMQ_SERVICE_HOST,
                                  "RABBITMQ_DEFAULT_VHOST": RABBITMQ_DEFAULT_VHOST,
                                  "RABBITMQ_QUEUES_USERNAME": RABBITMQ_USERNAME,
                                  "RABBITMQ_QUEUES_PASSWORD": RABBITMQ_PASSWORD,
                                  "VCS_INSTANCES_FILE_PATH": VCS_INSTANCES_FILE_PATH}):
    from vcs_scraper.repository_collector import common  # noqa: E402  # isort:skip

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

    btbk_vcs_instance = VCSInstance(name="test_name2",
                                    provider_type=BITBUCKET,
                                    hostname="fake.bitbucket.com",
                                    port=443,
                                    scheme="https",
                                    username="VCS_INSTANCE_USERNAME",
                                    token="VCS_INSTANCE_TOKEN",
                                    exceptions=[],
                                    scope=[])


@patch.object(Celery, "send_task")
def test_send_tasks_to_celery_queue(celery_send_task):
    task_name = "celery_task1"
    repository_queue = REPOSITORY_QUEUE
    project_tasks = []

    branches = [BranchInfo(branch_id="/ref/head/main",
                           last_scanned_commit="abc",
                           repository_info_id=1,
                           branch_name="main"),
                BranchInfo(branch_id="/ref/head/master",
                           last_scanned_commit="xyz",
                           repository_info_id=2,
                           branch_name="master")]

    repository_info = RepositoryInfo(project_key="PROJ", repository_name="name", branches_info=branches,
                                     repository_url="www.fake-vcs.com/proj/name", repository_id="xyz",
                                     vcs_instance_name="test server")

    project_tasks.append(repository_info)

    common.send_tasks_to_celery_queue(task_name, repository_queue, project_tasks)
    assert celery_send_task.call_count == len(project_tasks)

    for index, send_task_call in enumerate(celery_send_task.call_args_list):
        args, kwargs = send_task_call
        assert args[0] == "celery_task1"
        assert kwargs["kwargs"]['repository_info'] == project_tasks[index].json()
        assert kwargs["queue"] == repository_queue


@patch.object(Celery, "send_task")
def test_send_tasks_to_celery_queue_without_tasks(celery_send_task):
    task_name = "celery_task1"
    repository_queue = REPOSITORY_QUEUE
    project_tasks = []

    common.send_tasks_to_celery_queue(task_name, repository_queue, project_tasks)
    assert celery_send_task.call_count == 0


@patch("vcs_scraper.vcs_connectors.azure_devops_connector.AzureDevopsConnector.get_repos")
def test_extract_ado_project_information_with_empty_project(mock_get):
    azure_devops_client = VCSConnectorFactory.create_client_from_vcs_instance(ado_vcs_instance)
    project_key = "mock_project_key"

    get_repos = list()
    mock_get.side_effect = [get_repos]

    project_tasks = common.extract_project_information(project_key, azure_devops_client, ado_vcs_instance.name)

    assert project_tasks == []


@patch("vcs_scraper.vcs_connectors.azure_devops_connector.AzureDevopsConnector.get_repos")
@patch("vcs_scraper.vcs_connectors.azure_devops_connector.AzureDevopsConnector.get_branches")
def test_extract_ado_project_information(mock_get_branches, mock_get_repos):
    azure_devops_client = VCSConnectorFactory.create_client_from_vcs_instance(ado_vcs_instance)
    project_key = "GRID0001"

    repository_information = {
        "project": {"name": "GRID0001"},
        "name": "repo1",
        "id": "1234",
        "web_url": "http://test.com/repo.git"
    }

    branches_information = [{"name": "feature", "commit": {"commit_id": "ABCDEFG"}},
                            {"name": "master", "commit": {"commit_id": "QRSTUVWXYZ"}}]

    get_repos = list([repository_information])
    mock_get_repos.side_effect = [get_repos]
    mock_get_branches.side_effect = [branches_information]

    with mock.patch.dict(os.environ, {"SCAN_ONLY_MASTER_BRANCH": "false"}):
        project_tasks = common.extract_project_information(project_key, azure_devops_client, ado_vcs_instance.name)

    assert len(project_tasks) == 1
    result = project_tasks[0]
    assert type(result) is RepositoryInfo
    assert result.repository_name == "repo1"
    assert result.project_key == project_key
    assert result.branches_info[0].branch_id == "feature"
    assert result.branches_info[0].last_scanned_commit == "ABCDEFG"
    assert result.branches_info[1].branch_id == "master"
    assert result.branches_info[1].last_scanned_commit == "QRSTUVWXYZ"


@patch("vcs_scraper.vcs_connectors.bitbucket_connector.BitbucketConnector.get_repos")
def test_extract_btbk_project_information_with_empty_project(mock_get):
    bitbucket_client = VCSConnectorFactory.create_client_from_vcs_instance(btbk_vcs_instance)
    project_key = "mock_project_key"

    get_repos = list()
    mock_get.side_effect = [get_repos]

    project_tasks = common.extract_project_information(project_key, bitbucket_client, btbk_vcs_instance.name)

    assert project_tasks == []


@patch("vcs_scraper.vcs_connectors.bitbucket_connector.BitbucketConnector.get_repos")
@patch("vcs_scraper.vcs_connectors.bitbucket_connector.BitbucketConnector.get_branches")
def test_extract_btbk_project_information(mock_get_branches, mock_get_repos):
    bitbucket_client = VCSConnectorFactory.create_client_from_vcs_instance(btbk_vcs_instance)
    project_key = "PROJ"

    repository_information = {
        "project": {"id": 1337, "key": project_key},
        "name": "repo1",
        "id": "1234",
        "links": {"clone": [{"href": "ssh://git@test.com/repo.git", "name": "ssh"},
                            {"href": "http://test.com/repo.git", "name": "http"}], "self": "bla"}
    }

    branches_information = [{"id": "features/1", "displayId": "1", "latestCommit": "ABCDEFG"},
                            {"id": "/refs/heads/main", "displayId": "main", "latestCommit": "QRSTUVWXYZ"}]

    get_repos = list([repository_information])
    mock_get_repos.side_effect = [get_repos]
    mock_get_branches.side_effect = [branches_information]

    with mock.patch.dict(os.environ, {"SCAN_ONLY_MASTER_BRANCH": "false"}):
        project_tasks = common.extract_project_information(project_key, bitbucket_client, btbk_vcs_instance.name)

    assert len(project_tasks) == 1
    result = project_tasks[0]
    assert type(result) is RepositoryInfo
    assert result.repository_name == "repo1"
    assert result.project_key == project_key
    assert result.branches_info[0].branch_id == "features/1"
    assert result.branches_info[0].last_scanned_commit == "ABCDEFG"
    assert result.branches_info[1].branch_id == "/refs/heads/main"
    assert result.branches_info[1].last_scanned_commit == "QRSTUVWXYZ"
