# pylint: disable=R0903
# First Party
from vcs_scanner.helpers.environment_wrapper import EnvironmentVariable

DEBUG_MODE = "DEBUG_MODE"

GITLEAKS_PATH = "GITLEAKS_PATH"

RABBITMQ_SERVICE_HOST = "RESC_RABBITMQ_SERVICE_HOST"
RABBITMQ_DEFAULT_VHOST = "RABBITMQ_DEFAULT_VHOST"
RABBITMQ_USERNAME = "RABBITMQ_USERNAME"
RABBITMQ_PASSWORD = "RABBITMQ_PASSWORD"
RABBITMQ_QUEUE = "RABBITMQ_QUEUE"

VCS_INSTANCES_FILE_PATH = "VCS_INSTANCES_FILE_PATH"

RESC_API_NO_AUTH_SERVICE_HOST = "RESC_API_NO_AUTH_SERVICE_HOST"
RESC_API_NO_AUTH_SERVICE_PORT = "RESC_API_NO_AUTH_SERVICE_PORT"


REQUIRED_ENV_VARS = [
    EnvironmentVariable(
        GITLEAKS_PATH,
        "The filepath for the gitleaks binary",
        required=True,
    ),
    EnvironmentVariable(
        RABBITMQ_SERVICE_HOST,
        "The hostname/IP address of the rabbitmq server.",
        required=True,
    ),
    EnvironmentVariable(
        RABBITMQ_DEFAULT_VHOST,
        "The virtual host name of the rabbitmq server.",
        required=True,
    ),
    EnvironmentVariable(
        DEBUG_MODE,
        "Show debug log statements, if set to '0' only INFO logs and above will be shown.",
        required=False,
        default="0",
    ),
    EnvironmentVariable(
        RESC_API_NO_AUTH_SERVICE_HOST,
        "URL of the RESC API authentication disabled endpoint",
        required=True,
    ),
    EnvironmentVariable(
        RESC_API_NO_AUTH_SERVICE_PORT,
        "PORT of the RESC API authentication disabled endpoint",
        default="8000",
    ),
    EnvironmentVariable(
        RABBITMQ_USERNAME,
        "The username used to connect to the rabbitmq queues.",
        required=True,
    ),
    EnvironmentVariable(
        RABBITMQ_PASSWORD,
        "The password used to connect to the rabbitmq queues.",
        required=True,
    ),
    EnvironmentVariable(
        RABBITMQ_QUEUE,
        "The rabbitmq queue to connect to.",
        required=True,
    ),
    EnvironmentVariable(
        VCS_INSTANCES_FILE_PATH,
        "The absolute path to the json file containing the vcs_instances_definitions",
        required=True,
    ),
]
