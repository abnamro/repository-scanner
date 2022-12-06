# coding=utf-8

# First Party
from resc_backend.helpers.environment_wrapper import EnvironmentVariable

RESC_RABBITMQ_SERVICE_HOST = "RESC_RABBITMQ_SERVICE_HOST"
RESC_RABBITMQ_SERVICE_PORT_MGMT = "RESC_RABBITMQ_SERVICE_PORT_MGMT"
RABBITMQ_DEFAULT_VHOST = "RABBITMQ_DEFAULT_VHOST"
RABBITMQ_DEFAULT_USER = "RABBITMQ_DEFAULT_USER"
RABBITMQ_DEFAULT_PASSWORD = "RABBITMQ_DEFAULT_PASS"
RABBITMQ_USERNAME = "RABBITMQ_USERNAME"
RABBITMQ_PASSWORD = "RABBITMQ_PASSWORD"
DEBUG_MODE = "DEBUG_MODE"

REQUIRED_ENV_VARS = [
    EnvironmentVariable(
        RESC_RABBITMQ_SERVICE_HOST,
        "The hostname/IP address of the rabbitmq server.",
        required=True,
    ),
    EnvironmentVariable(
        RESC_RABBITMQ_SERVICE_PORT_MGMT,
        "The port on which the rabbitmq mgmt server is running.",
        required=True,
    ),
    EnvironmentVariable(
        RABBITMQ_DEFAULT_VHOST,
        "The virtual host name of the rabbitmq server.",
        required=True,
    ),
    EnvironmentVariable(
        RABBITMQ_DEFAULT_USER,
        "The username used to connect to the rabbitmq server.",
        required=True,
    ),
    EnvironmentVariable(
        RABBITMQ_DEFAULT_PASSWORD,
        "The password used to connect to the rabbitmq server.",
        required=True,
    ),
    EnvironmentVariable(
        RABBITMQ_USERNAME,
        "The username used to connect to the rabbitmq queue",
        required=True,
    ),
    EnvironmentVariable(
        RABBITMQ_PASSWORD,
        "The password used to connect to the rabbitmq queue",
        required=True,
    ),
    EnvironmentVariable(
        DEBUG_MODE,
        "Show debug log statements, if set to '0' only INFO logs and above will be shown.",
        required=False,
        default="0",
    )
]
