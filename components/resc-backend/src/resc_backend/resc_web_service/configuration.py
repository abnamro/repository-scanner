# coding=utf-8
# First Party
from resc_backend.helpers.environment_wrapper import EnvironmentVariable

RESC_REDIS_SERVICE_HOST = 'RESC_REDIS_SERVICE_HOST'
RESC_REDIS_SERVICE_PORT = 'RESC_REDIS_SERVICE_PORT'
REDIS_PASSWORD = 'REDIS_PASSWORD'

REQUIRED_ENV_VARS = [
    EnvironmentVariable(
        RESC_REDIS_SERVICE_HOST,
        "The hostname/IP address of the REDIS server.",
        required=True,
    ),
    EnvironmentVariable(
        RESC_REDIS_SERVICE_PORT,
        "The port on which the REDIS server is running.",
        required=True,
    ),
    EnvironmentVariable(
        REDIS_PASSWORD,
        "The REDIS authentication secret.",
        required=True,
    ),
]
