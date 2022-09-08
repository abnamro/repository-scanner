# pylint: disable=E1101
# Standard Library
import logging

# Third Party
import requests
from requests.adapters import HTTPAdapter
from requests.auth import HTTPBasicAuth
from urllib3 import Retry

# First Party
from repository_scanner_backend.common import initialise_logs
from repository_scanner_backend.constants import LOG_FILE_PATH_RABBITMQ, PROJECT_QUEUE, REPOSITORY_QUEUE
from repository_scanner_backend.helpers.environment_wrapper import validate_environment
from repository_scanner_backend.helpers.rabbitmq.configuration import (
    RABBITMQ_DEFAULT_PASSWORD,
    RABBITMQ_DEFAULT_USER,
    RABBITMQ_DEFAULT_VHOST,
    RABBITMQ_PASSWORD,
    RABBITMQ_USERNAME,
    REQUIRED_ENV_VARS
)

env_variables = validate_environment(REQUIRED_ENV_VARS)
logger_config = initialise_logs(LOG_FILE_PATH_RABBITMQ)
logger = logging.getLogger(__name__)


def wait_for_rabbitmq_server_to_up(rabbitmq_api_base_url: str) -> bool:
    """
        This function returns true once the RabbitMQ server is up.
    :param rabbitmq_api_base_url:
        RabbitMQ API base url
    """
    rabbitmq_admin_user = f"{env_variables[RABBITMQ_DEFAULT_USER]}"
    rabbitmq_admin_password = f"{env_variables[RABBITMQ_DEFAULT_PASSWORD]}"

    session = requests.Session()
    retries = Retry(total=100,
                    backoff_factor=1,
                    status_forcelist=[500, 502, 503, 504])
    uri = rabbitmq_api_base_url + "/api/health/checks/alarms"
    session.mount("http://", HTTPAdapter(max_retries=retries))
    response = session.get(uri,
                           auth=HTTPBasicAuth(rabbitmq_admin_user, rabbitmq_admin_password))

    if hasattr(response, "status_code") and int(response.status_code) == 200:
        logger.debug("Rabbitmq server is up.")
        return True
    logger.error(f"Rabbitmq server is down, HTTP status: '{response.status_code}'")
    return False


def create_user(rabbitmq_api_base_url: str, username: str, password: str, role: str) -> bool:
    """
        Creates a user in RabbitMQ server, it would return true if the operation was a success, false otherwise
    :param rabbitmq_api_base_url:
        RabbitMQ API base url
    :param username:
        Username to be created
    :param password:
        Password of the user to be created
    :param role:
        Role of the user to be created
    :return: True if user creation is successful else returns False.
    """
    rabbitmq_admin_user = f"{env_variables[RABBITMQ_DEFAULT_USER]}"
    rabbitmq_admin_password = f"{env_variables[RABBITMQ_DEFAULT_PASSWORD]}"

    uri = rabbitmq_api_base_url + "/api/users/" + username
    user_data = {"password": password, "tags": role}
    response = requests.put(uri, json=user_data,
                            auth=HTTPBasicAuth(rabbitmq_admin_user, rabbitmq_admin_password))

    if hasattr(response, "status_code") and int(response.status_code) == 201:
        logger.info(f"User: {username} with role: {role} created successfully.")
        return True
    if hasattr(response, "status_code") and int(response.status_code) == 204:
        logger.info(f"User: {username} with role: {role} already exists.")
        return True
    logger.error(f"Failed while creating user: '{username}' "
                 f"with role: '{role}' "
                 f", HTTP status: '{response.status_code}'")
    return False


def set_resource_permissions(rabbitmq_api_base_url: str, v_host: str, username: str, configure_resources_regex: str,
                             read_resources_regex: str, write_resources_regex: str) -> bool:
    """
        Sets permission for resources, it would return true if the operation was a success, false otherwise
    :param rabbitmq_api_base_url:
        RabbitMQ API base url
    :param v_host:
        Virtual host name of the RabbitMQ server
    :param username:
        User whose permission needs to set
    :param configure_resources_regex:
        Regex of the resources for which permission needs to set
    :param read_resources_regex:
        Regex of read permission
    :param write_resources_regex:
        Regex of write permission
    :return: True if permission assigned to user is successful else returns False.
    """
    rabbitmq_admin_user = f"{env_variables[RABBITMQ_DEFAULT_USER]}"
    rabbitmq_admin_password = f"{env_variables[RABBITMQ_DEFAULT_PASSWORD]}"

    uri = rabbitmq_api_base_url + "/api/permissions/" + v_host + "/" + username
    permission_data = {"configure": configure_resources_regex, "write": write_resources_regex,
                       "read": read_resources_regex}

    response = requests.put(uri, json=permission_data,
                            auth=HTTPBasicAuth(rabbitmq_admin_user, rabbitmq_admin_password))
    if hasattr(response, "status_code") and int(response.status_code) == 201:
        logger.debug(f"vHost permission successfully assigned to user: {username} for vHost: {v_host}.")
        return True
    logger.error(f"Failed while assigning vhost permission to user: '{username}' "
                 f"for vhost: '{v_host}' "
                 f", HTTP status: '{response.status_code}'")
    return False


def set_topic_permissions(rabbitmq_api_base_url: str, v_host: str, username: str, topic_name: str, allow_read: bool,
                          allow_write: bool) -> bool:
    """
        Sets permission for topics, it would return true if the operation was a success, false otherwise
    :param rabbitmq_api_base_url:
        RabbitMQ API base url
    :param v_host:
        Virtual host name of the RabbitMQ server
    :param username:
        User whose permission needs to set
    :param topic_name:
        Name of the topic for which permission needs to set
    :param allow_read:
        Read permission allowed or not
    :param allow_write:
        Write permission allowed or not
    :return: True if topic permission assigned to user is successful else returns False.
    """
    permission_allow = ".*"
    permission_deny = "^$"
    read_permission = permission_deny
    write_permission = permission_deny

    if allow_read:
        read_permission = permission_allow
    if allow_write:
        write_permission = permission_allow

    rabbitmq_admin_user = f"{env_variables[RABBITMQ_DEFAULT_USER]}"
    rabbitmq_admin_password = f"{env_variables[RABBITMQ_DEFAULT_PASSWORD]}"

    uri = rabbitmq_api_base_url + "/api/topic-permissions/" + v_host + "/" + username
    topic_permission_data = {"exchange": topic_name, "write": write_permission, "read": read_permission}

    response = requests.put(uri, json=topic_permission_data,
                            auth=HTTPBasicAuth(rabbitmq_admin_user, rabbitmq_admin_password))

    if hasattr(response, "status_code") and (int(response.status_code) == 201 or int(response.status_code) == 204):
        logger.debug(
            f"Topic permission successfully assigned to user: {username} for topic: {topic_name} in vhost: {v_host}.")
        return True
    logger.error(f"Failed while assigning topic permission to user: '{username}' "
                 f"with vhost: '{v_host}' "
                 f"for topic: '{topic_name}' "
                 f", HTTP status: '{response.status_code}'")
    return False


def create_queue_user_and_set_permission(rabbitmq_api_base_url: str):
    """
        This function creates user for queue and assigns required permission.
    :param rabbitmq_api_base_url:
        RabbitMQ API base url
    """
    rabbitmq_vhost = f"{env_variables[RABBITMQ_DEFAULT_VHOST]}"
    queue_user = f"{env_variables[RABBITMQ_USERNAME]}"
    queue_password = f"{env_variables[RABBITMQ_PASSWORD]}"

    user_created = create_user(rabbitmq_api_base_url=rabbitmq_api_base_url, username=queue_user,
                               password=queue_password, role="monitoring")
    if user_created:
        set_resource_permissions(rabbitmq_api_base_url=rabbitmq_api_base_url, v_host=rabbitmq_vhost,
                                 username=queue_user,
                                 configure_resources_regex=f"^({PROJECT_QUEUE}|{REPOSITORY_QUEUE}"
                                                           f"|.*celery.*)$",
                                 read_resources_regex=f"^{PROJECT_QUEUE}|{REPOSITORY_QUEUE}"
                                                      f"|.*celery.*$",
                                 write_resources_regex=f"^{PROJECT_QUEUE}|{REPOSITORY_QUEUE}"
                                                       f"|amq.default|.*celery.*$")
        set_topic_permissions(rabbitmq_api_base_url=rabbitmq_api_base_url, v_host=rabbitmq_vhost, username=queue_user,
                              topic_name=f"{PROJECT_QUEUE}", allow_read=True, allow_write=True)
        set_topic_permissions(rabbitmq_api_base_url=rabbitmq_api_base_url, v_host=rabbitmq_vhost, username=queue_user,
                              topic_name=f"{REPOSITORY_QUEUE}", allow_read=True, allow_write=True)
