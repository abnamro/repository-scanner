# Standard Library
import logging
from typing import List

# Third Party
import requests

# First Party
from vcs_scraper.common import create_celery_client, load_vcs_instances_into_map
from vcs_scraper.configuration import (
    RABBITMQ_DEFAULT_VHOST,
    RABBITMQ_QUEUES_PASSWORD,
    RABBITMQ_QUEUES_USERNAME,
    REQUIRED_ENV_VARS,
    RESC_RABBITMQ_SERVICE_HOST,
    VCS_INSTANCES_FILE_PATH
)
from vcs_scraper.constants import PROJECT_QUEUE, REPOSITORY_QUEUE, SECRET_SCANNER_TASK_NAME
from vcs_scraper.environment_wrapper import validate_environment
from vcs_scraper.model import Repository
from vcs_scraper.vcs_connectors.vcs_connector_factory import VCSConnectorFactory

logger = logging.getLogger(__name__)
env_variables = validate_environment(REQUIRED_ENV_VARS)
celery_client = create_celery_client("repository_collector", env_variables[RABBITMQ_QUEUES_USERNAME],
                                     env_variables[RABBITMQ_QUEUES_PASSWORD],
                                     env_variables[RESC_RABBITMQ_SERVICE_HOST],
                                     env_variables[RABBITMQ_DEFAULT_VHOST])


def extract_project_information(project_key, vcs_client, vcs_instance_name):
    """
    From a given vcs instance and a  project_key, this function returns a list containing generic
    info about of its repositories.
    """
    logger.info(f"Fetching repositories for project: '{project_key}' in vcs instance '{vcs_instance_name}'")
    project_repositories = vcs_client.get_repos(project_key)
    logger.info(f"Fetched {len(project_repositories)} repositories for project: '{project_key}'")
    project_tasks = []
    for repository in project_repositories:
        try:
            logger.info(f"Fetching latest commit for repository: '{project_key}/{repository['name']}'")
            latest_commit = vcs_client.get_latest_commit(project_key=project_key, repository_id=repository["name"])
            task_parameters = vcs_client.export_repository(repository, latest_commit, vcs_instance_name)
            if latest_commit:
                project_tasks.append(task_parameters)
                logger.info(f"Information for repository: '{project_key}/{repository['name']}' "
                            f"was fetched successfully")
            else:
                # Repository has no commits, will not forward to scanner
                logger.info(f"Repository: '{project_key}/{repository['name']}' has no commits, skipping")

        except requests.exceptions.HTTPError as http_exception:
            logger.error(
                f"Error while processing repository '{project_key}/{repository['name']}':"
                f" Unable to obtain the repository's latest commit: {http_exception}")
    return project_tasks


def send_tasks_to_celery_queue(task_name: str, queue_name: str, project_tasks: List[Repository]):
    for task in project_tasks:
        celery_client.send_task(task_name, kwargs={"repository": task.json()}, queue=queue_name)


@celery_client.task(Queue=PROJECT_QUEUE)
def collect_repositories(project_key, vcs_instance_name):
    """
    Celery worker which takes as input a project ID and collects the required information about all of its repos.
    """
    vcs_instances_map = load_vcs_instances_into_map(env_variables[VCS_INSTANCES_FILE_PATH])

    logger.info(f"Project processor received an azure project key: '{project_key}'")

    vcs_client = VCSConnectorFactory.create_client_from_vcs_instance(vcs_instances_map[vcs_instance_name])
    project_tasks = extract_project_information(project_key, vcs_client, vcs_instance_name)
    send_tasks_to_celery_queue(SECRET_SCANNER_TASK_NAME, REPOSITORY_QUEUE, project_tasks)
