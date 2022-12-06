# Standard Library
import os
from unittest import mock
from unittest.mock import patch

# Third Party
from celery import Celery

# First Party
from vcs_scraper.constants import AZURE_DEVOPS, BITBUCKET, PROJECT_QUEUE
from vcs_scraper.vcs_instances_parser import VCSInstance

RESC_RABBITMQ_SERVICE_HOST = "fake-rabbitmq-host.com"
RABBITMQ_DEFAULT_VHOST = "vhost"
RABBITMQ_QUEUES_USERNAME = "fake_rabbituser"
RABBITMQ_QUEUES_PASSWORD = "fake_password"
VCS_INSTANCES_FILE_PATH = "fake_path.json"

with mock.patch.dict(os.environ, {"RESC_RABBITMQ_SERVICE_HOST": RESC_RABBITMQ_SERVICE_HOST,
                                  "RABBITMQ_DEFAULT_VHOST": RABBITMQ_DEFAULT_VHOST,
                                  "RABBITMQ_QUEUES_USERNAME": RABBITMQ_QUEUES_USERNAME,
                                  "RABBITMQ_QUEUES_PASSWORD": RABBITMQ_QUEUES_PASSWORD,
                                  "VCS_INSTANCES_FILE_PATH": VCS_INSTANCES_FILE_PATH}):
    from vcs_scraper.project_collector import common  # noqa: E402  # isort:skip

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
    btbk_scoped_vcs_instance = VCSInstance(name="test_name2",
                                           provider_type=BITBUCKET,
                                           hostname="fake.bitbucket.com",
                                           port=443,
                                           scheme="https",
                                           username="VCS_INSTANCE_USERNAME",
                                           token="VCS_INSTANCE_TOKEN",
                                           exceptions=[],
                                           scope=["project1"])

    btbk_with_exceptions_vcs_instance = VCSInstance(name="test_name2",
                                                    provider_type=BITBUCKET,
                                                    hostname="fake.bitbucket.com",
                                                    port=443,
                                                    scheme="https",
                                                    username="VCS_INSTANCE_USERNAME",
                                                    token="VCS_INSTANCE_TOKEN",
                                                    exceptions=["project1"],
                                                    scope=[])


@patch("vcs_scraper.vcs_connectors.azure_devops_connector.AzureDevopsConnector.get_all_projects")
@patch.object(Celery, "send_task")
def test_collect_ado_projects_with_projects(celery_send_task, get_all_projects):

    all_projects = ["project1", "project2"]
    get_all_projects.side_effect = [all_projects]
    common.collect_projects_from_vcs_instance(ado_vcs_instance)
    assert celery_send_task.call_count == len(all_projects)
    for index, send_task_call in enumerate(celery_send_task.call_args_list):
        args, kwargs = send_task_call
        assert args[0] == "vcs_scraper.repository_collector.common.collect_repositories"
        assert kwargs["kwargs"]["project_key"] == all_projects[index]
        assert kwargs["queue"] == PROJECT_QUEUE


@patch("vcs_scraper.vcs_connectors.azure_devops_connector.AzureDevopsConnector.get_all_projects")
@patch.object(Celery, "send_task")
def test_collect_ado_projects_without_projects(celery_send_task, get_all_projects):
    all_projects = list()
    get_all_projects.side_effect = [all_projects]

    common.collect_projects_from_vcs_instance(ado_vcs_instance)

    assert celery_send_task.call_count == 0


@patch("vcs_scraper.vcs_connectors.bitbucket_connector.BitbucketConnector.get_all_projects")
@patch.object(Celery, "send_task")
def test_collect_btbk_projects_with_projects(celery_send_task, get_all_projects):
    all_projects = ["project1", "project2"]
    get_all_projects.side_effect = [all_projects]
    common.collect_projects_from_vcs_instance(btbk_vcs_instance)
    assert celery_send_task.call_count == len(all_projects)
    for index, send_task_call in enumerate(celery_send_task.call_args_list):
        args, kwargs = send_task_call
        assert args[0] == "vcs_scraper.repository_collector.common.collect_repositories"
        assert kwargs["kwargs"]["project_key"] == all_projects[index]
        assert kwargs["queue"] == PROJECT_QUEUE


@patch("vcs_scraper.vcs_connectors.bitbucket_connector.BitbucketConnector.get_all_projects")
@patch.object(Celery, "send_task")
def test_collect_btbk_projects_without_projects(celery_send_task, get_all_projects):
    all_projects = list()
    get_all_projects.side_effect = [all_projects]

    common.collect_projects_from_vcs_instance(btbk_vcs_instance)

    assert celery_send_task.call_count == 0


@patch("vcs_scraper.vcs_connectors.bitbucket_connector.BitbucketConnector.project_exists")
@patch("vcs_scraper.vcs_connectors.bitbucket_connector.BitbucketConnector.get_all_projects")
@patch.object(Celery, "send_task")
def test_collect_btbk_projects_with_scope(celery_send_task, all_projects, project_exists):
    def mock_project_exists(project_key):
        return project_key == "project1"
    assert btbk_scoped_vcs_instance.scope == ["project1"]

    project_exists.side_effect = mock_project_exists
    common.collect_projects_from_vcs_instance(btbk_scoped_vcs_instance)
    assert celery_send_task.call_count == 1
    assert celery_send_task.call_args_list[0][1]["kwargs"]["project_key"] == "project1"
    assert not all_projects.called


@patch("vcs_scraper.vcs_connectors.bitbucket_connector.BitbucketConnector.get_all_projects")
@patch.object(Celery, "send_task")
def test_collect_btbk_projects_with_exceptions(celery_send_task, get_all_projects):
    all_projects = ["project1", "project2"]
    get_all_projects.side_effect = [all_projects]
    common.collect_projects_from_vcs_instance(btbk_with_exceptions_vcs_instance)
    assert celery_send_task.call_count == 1
    assert celery_send_task.call_args_list[0][1]["kwargs"]["project_key"] == "project2"
