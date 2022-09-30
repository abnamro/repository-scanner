# Standard Library
import os

# Third Party
from mock import mock

# First Party
from vcs_scraper.constants import AZURE_DEVOPS, BITBUCKET
from vcs_scraper.model import VCSInstance
from vcs_scraper.vcs_connectors.azure_devops_connector import AzureDevopsConnector
from vcs_scraper.vcs_connectors.bitbucket_connector import BitbucketConnector
from vcs_scraper.vcs_connectors.vcs_connector_factory import VCSConnectorFactory

with mock.patch.dict(os.environ, {"VCS_INSTANCE_TOKEN": "token123", "VCS_INSTANCE_USERNAME": "user123"}):
    ado_vcs_instance = VCSInstance(name="test_name1",
                                   provider_type=AZURE_DEVOPS,
                                   hostname="fake.ado.com",
                                   port=443,
                                   scheme="https",
                                   username="VCS_INSTANCE_USERNAME",
                                   token="VCS_INSTANCE_TOKEN",
                                   exceptions=[],
                                   scope=[])

    btbk_vcs_instance = VCSInstance(name="test_name2",
                                    provider_type=BITBUCKET,
                                    hostname="fake.bitbucket.com",
                                    port=443,
                                    scheme="https",
                                    username="VCS_INSTANCE_USERNAME",
                                    token="VCS_INSTANCE_TOKEN",
                                    exceptions=[],
                                    scope=[])


def test_create_bitbucket_vcs_connector():
    vcs_client = VCSConnectorFactory.create_client_from_vcs_instance(btbk_vcs_instance)
    assert isinstance(vcs_client, BitbucketConnector)


def test_create_azure_ado_vcs_connector():
    vcs_client = VCSConnectorFactory.create_client_from_vcs_instance(ado_vcs_instance)
    assert isinstance(vcs_client, AzureDevopsConnector)
