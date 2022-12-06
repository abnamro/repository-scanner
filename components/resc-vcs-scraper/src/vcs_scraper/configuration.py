# coding=utf-8

# First Party
from vcs_scraper.environment_wrapper import EnvironmentVariable

RESC_RABBITMQ_SERVICE_HOST = "RESC_RABBITMQ_SERVICE_HOST"
RABBITMQ_DEFAULT_VHOST = "RABBITMQ_DEFAULT_VHOST"
RABBITMQ_QUEUES_USERNAME = "RABBITMQ_QUEUES_USERNAME"
RABBITMQ_QUEUES_PASSWORD = "RABBITMQ_QUEUES_PASSWORD"
PROJECT_QUEUE = "PROJECT_QUEUE"
VCS_INSTANCES_FILE_PATH = "VCS_INSTANCES_FILE_PATH"

DEBUG_MODE = "DEBUG_MODE"

REQUIRED_ENV_VARS = [

    EnvironmentVariable(
        DEBUG_MODE,
        "Show debug log statements, if set to '0' only INFO logs and above will be shown.",
        required=False,
        default="0",
    ),
    EnvironmentVariable(
        RABBITMQ_QUEUES_USERNAME,
        "The username used to connect to the rabbitmq project collector and repository collector topics.",
        required=True,
    ),
    EnvironmentVariable(
        RABBITMQ_QUEUES_PASSWORD,
        "The password used to connect to the rabbitmq project collector and repository collector topics.",
        required=True,
    ),
    EnvironmentVariable(
        RESC_RABBITMQ_SERVICE_HOST,
        "The hostname/IP address of the rabbitmq server.",
        required=True,
    ),
    EnvironmentVariable(
        RABBITMQ_DEFAULT_VHOST,
        "The virtual host name of the rabbitmq server.",
        required=True,
    ),
    EnvironmentVariable(
        VCS_INSTANCES_FILE_PATH,
        "The absolute path to the json file containing the vcs_instances_definitions",
        required=True,
    ),
]
