# First Party
from vcs_scraper.constants import AZURE_DEVOPS, BITBUCKET, GITHUB_PUBLIC
from vcs_scraper.vcs_connectors.azure_devops_connector import AzureDevopsConnector
from vcs_scraper.vcs_connectors.bitbucket_connector import BitbucketConnector
from vcs_scraper.vcs_connectors.github_public_connector import GithubPublicConnector
from vcs_scraper.vcs_instances_parser import VCSInstance


class VCSConnectorFactory:

    @staticmethod
    def create_client_from_vcs_instance(vcs_instance: VCSInstance):
        if vcs_instance.provider_type == BITBUCKET:
            return BitbucketConnector.create_client_from_vcs_instance(vcs_instance)
        if vcs_instance.provider_type == AZURE_DEVOPS:
            return AzureDevopsConnector.create_client_from_vcs_instance(vcs_instance)
        if vcs_instance.provider_type == GITHUB_PUBLIC:
            return GithubPublicConnector.create_client_from_vcs_instance(vcs_instance)
        raise NotImplementedError(f"Provider {vcs_instance.provider_type} is not supported")
