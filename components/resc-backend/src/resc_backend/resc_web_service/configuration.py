# coding=utf-8

# First Party
from resc_backend.helpers.environment_wrapper import EnvironmentVariable, validate_environment

RESC_REDIS_SERVICE_HOST = 'RESC_REDIS_SERVICE_HOST'
RESC_REDIS_PORT = 'RESC_REDIS_PORT'
REDIS_PASSWORD = 'REDIS_PASSWORD'
RESC_REDIS_CACHE_ENABLE = 'RESC_REDIS_CACHE_ENABLE'

REQUIRED_ENV_VARS = [
    EnvironmentVariable(
        RESC_REDIS_CACHE_ENABLE,
        "The REDIS authentication secret.",
        required=True,
    )
]

env_variables = validate_environment(REQUIRED_ENV_VARS)

cache_enabled = f"{env_variables[RESC_REDIS_CACHE_ENABLE]}"


if cache_enabled is True:
    REQUIRED_ENV_VARS = [
        EnvironmentVariable(
            RESC_REDIS_SERVICE_HOST,
            "The hostname/IP address of the REDIS server.",
            required=True,
        ),
        EnvironmentVariable(
            RESC_REDIS_PORT,
            "The port on which the REDIS server is running.",
            required=True,
        ),
        EnvironmentVariable(
            REDIS_PASSWORD,
            "The REDIS authentication secret.",
            required=True,
        ),
    ]
