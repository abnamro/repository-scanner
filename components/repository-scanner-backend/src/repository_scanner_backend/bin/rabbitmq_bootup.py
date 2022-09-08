# pylint: disable=E1101
# Standard Library
import logging
import sys
from argparse import ArgumentParser, Namespace

# First Party
from repository_scanner_backend.helpers.environment_wrapper import validate_environment
from repository_scanner_backend.helpers.rabbitmq.configuration import (
    REQUIRED_ENV_VARS,
    RESC_RABBITMQ_SERVICE_HOST,
    RESC_RABBITMQ_SERVICE_PORT_MGMT
)
from repository_scanner_backend.helpers.rabbitmq.rabbitmq_initialization import (
    create_queue_user_and_set_permission,
    wait_for_rabbitmq_server_to_up
)

env_variables = validate_environment(REQUIRED_ENV_VARS)
logger = logging.getLogger(__name__)


def create_cli_argparser() -> ArgumentParser:
    rabbitmq_service_host = f"{env_variables[RESC_RABBITMQ_SERVICE_HOST]}"
    rabbitmq_service_port = f"{env_variables[RESC_RABBITMQ_SERVICE_PORT_MGMT]}"
    rabbitmq_api_base_url = "http://" + rabbitmq_service_host + ":" + rabbitmq_service_port

    parser: ArgumentParser = ArgumentParser()
    parser.add_argument("--rabbitmq-url", type=str, default=rabbitmq_api_base_url,
                        help="RabbitMQ URL")

    return parser


def validate_cli_arguments(args: Namespace):  # pylint: disable=R0912
    valid_arguments = True
    if not args.rabbitmq_url:
        logger.error("RabbtMQ URL needs to be specified")
        valid_arguments = False
    if not valid_arguments:
        return False
    return args


def bootstrap_rabbitmq_users():
    """
    This function creates users in RabbitMQ server along with required permissions.
    """
    parser: ArgumentParser = create_cli_argparser()
    args: Namespace = parser.parse_args()
    args = validate_cli_arguments(args)
    if not args:
        logger.error("CLI arguments validation failed while bootstrapping rabbitmq users")
        sys.exit(-1)

    server_up = wait_for_rabbitmq_server_to_up(rabbitmq_api_base_url=args.rabbitmq_url)
    if not server_up:
        raise Exception("Wait for rabbitmq server to up has been failed.")
    create_queue_user_and_set_permission(rabbitmq_api_base_url=args.rabbitmq_url)
