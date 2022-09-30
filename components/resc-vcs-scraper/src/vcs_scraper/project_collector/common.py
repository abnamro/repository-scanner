# Standard Library
import logging

# Third Party
from tenacity import RetryError, Retrying, stop_after_attempt, wait_exponential

# First Party
from vcs_scraper.common import create_celery_client, initialise_logs, load_vcs_instances_into_map
from vcs_scraper.configuration import (
    DEBUG_MODE,
    RABBITMQ_DEFAULT_VHOST,
    RABBITMQ_QUEUES_PASSWORD,
    RABBITMQ_QUEUES_USERNAME,
    REQUIRED_ENV_VARS,
    RESC_RABBITMQ_SERVICE_HOST,
    VCS_INSTANCES_FILE_PATH
)
from vcs_scraper.constants import LOG_FILE_PATH_PRJ_COLLECTOR, PROJECT_QUEUE
from vcs_scraper.environment_wrapper import validate_environment
from vcs_scraper.vcs_connectors.vcs_connector_factory import VCSConnectorFactory
from vcs_scraper.vcs_instances_parser import VCSInstance

env_variables = validate_environment(REQUIRED_ENV_VARS)
logger_config = initialise_logs(LOG_FILE_PATH_PRJ_COLLECTOR, env_variables[DEBUG_MODE])
logger = logging.getLogger(__name__)


def collect_projects_from_vcs_instance(vcs_instance: VCSInstance) -> None:
    """
    Collects a list of all projects in the provided vcs instance and sends them to a RabbitMQ as celery tasks.
    """

    destination_message_queue = PROJECT_QUEUE

    task_name = "vcs_scraper.repository_collector.common.collect_repositories"
    vcs_client = VCSConnectorFactory.create_client_from_vcs_instance(vcs_instance)
    celery_client = create_celery_client("project_collector", env_variables[RABBITMQ_QUEUES_USERNAME],
                                         env_variables[RABBITMQ_QUEUES_PASSWORD],
                                         env_variables[RESC_RABBITMQ_SERVICE_HOST],
                                         env_variables[RABBITMQ_DEFAULT_VHOST])
    projects_to_scrape = []
    if vcs_instance.scope:
        logger.info(f"Checking if all projects within the scope exist in {vcs_client.url}")
        for project_in_scope in vcs_instance.scope:
            if vcs_client.project_exists(project_in_scope):
                logger.debug(f"Project '{project_in_scope}' is present in {vcs_client.url}")
                projects_to_scrape.append(project_in_scope)
            else:
                logger.warning(f"Project '{project_in_scope}' is not present in {vcs_client.url}")

    else:
        logger.info(f"Fetching list of all projects from {vcs_client.url}")
        projects_to_scrape = vcs_client.get_all_projects()
    projects_to_scrape_count = len(projects_to_scrape)
    logger.info(f"{projects_to_scrape_count} projects fetched successfully from '{vcs_client.url}'.")
    logger.info("Sending projects to the 'projects' queue.")
    projects_sent = 0
    for project_name in projects_to_scrape:
        if vcs_instance.exceptions:
            if project_name in vcs_instance.exceptions:
                logger.info(f"Skipping project {project_name} because it is within the exceptions.")
                continue
        try:
            for attempt in Retrying(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(100)):
                with attempt:
                    try:
                        celery_client.send_task(task_name, kwargs={"project_key": project_name,
                                                                   "vcs_instance_name": vcs_instance.name},
                                                queue=destination_message_queue)
                    except Exception as exc:
                        logger.error(f"{exc} sending '{project_name}' to 'projects'. Retrying ...")
                        raise
            projects_sent += 1
            logger.info(f"Project '{project_name}' was sent successfully.")
        except RetryError as exc:
            raise SystemExit(f"Error while sending project '{project_name}' to the 'projects' : "
                             f"retry timed out") from exc

    logger.info(f"{projects_sent} Projects sent successfully to the 'projects' "
                f"queue out of {projects_to_scrape_count} projects.")


def collect_all_projects():

    vcs_instances_map = load_vcs_instances_into_map(env_variables[VCS_INSTANCES_FILE_PATH])

    for vcs_instance in vcs_instances_map:

        collect_projects_from_vcs_instance(vcs_instances_map[vcs_instance])
