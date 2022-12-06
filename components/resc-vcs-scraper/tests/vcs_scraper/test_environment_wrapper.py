# Standard Library
import os
import sys
from unittest import TestCase, mock

# Third Party
import requests

# First Party
from vcs_scraper.configuration import REQUIRED_ENV_VARS
from vcs_scraper.constants import BITBUCKET
from vcs_scraper.vcs_connectors.vcs_connector_factory import VCSConnectorFactory
from vcs_scraper.vcs_instances_parser import VCSInstance

sys.path.insert(0, "src")
from vcs_scraper.environment_wrapper import validate_environment  # noqa: E402  # isort:skip


RESC_RABBITMQ_SERVICE_HOST = "fake-rabbitmq-host.com"
RABBITMQ_DEFAULT_VHOST = "vhost"


def test_validate_environment():
    env_variables = validate_environment(REQUIRED_ENV_VARS)
    assert env_variables["RESC_RABBITMQ_SERVICE_HOST"] == RESC_RABBITMQ_SERVICE_HOST
    assert env_variables["RABBITMQ_DEFAULT_VHOST"] == RABBITMQ_DEFAULT_VHOST


class ErrorTests(TestCase):
    # Make sure to set required env vars to empty first
    @mock.patch.dict(os.environ, {"RESC_RABBITMQ_SERVICE_HOST": ""})
    def test_validate_environment_required(self):
        self.assertRaises(EnvironmentError, validate_environment,
                          REQUIRED_ENV_VARS)


def test_create_bitbucket_client_from_env():
    with mock.patch.dict(os.environ, {"VCS_INSTANCE_TOKEN": "token123", "VCS_INSTANCE_USERNAME": "user123"}):
        vcs_instance = VCSInstance(name="test_name",
                                   provider_type=BITBUCKET,
                                   hostname="fake.bitbucket.com",
                                   port=443,
                                   scheme="https",
                                   username="VCS_INSTANCE_USERNAME",
                                   token="VCS_INSTANCE_TOKEN",
                                   exceptions=[],
                                   scope=[],)
    bitbucket_client = VCSConnectorFactory.create_client_from_vcs_instance(vcs_instance)
    session = requests.Session()
    session.headers['Authorization'] = f'Bearer {vcs_instance.token}'
    assert bitbucket_client.url == f"{vcs_instance.scheme}://{vcs_instance.hostname}:{vcs_instance.port}"
    assert bitbucket_client.api_client.url == bitbucket_client.url
    assert bitbucket_client.api_client._session.headers['Authorization'] == session.headers['Authorization']
