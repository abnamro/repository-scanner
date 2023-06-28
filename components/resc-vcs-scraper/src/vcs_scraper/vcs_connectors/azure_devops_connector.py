# Standard Library
import logging
from typing import Dict

# Third Party
from azure.devops.connection import Connection
from azure.devops.exceptions import AzureDevOpsServiceError
from azure.devops.released.core.core_client import CoreClient
from msrest.authentication import BasicAuthentication
from msrest.exceptions import ClientRequestError

# First Party
from vcs_scraper.model import Repository
from vcs_scraper.vcs_connectors.azure_devops_data_mapper import map_azure_devops_repository
from vcs_scraper.vcs_connectors.vcs_connector import VCSConnector
from vcs_scraper.vcs_instances_parser import VCSInstance

logger = logging.getLogger(__name__)


class AzureDevopsConnector(VCSConnector):
    def __init__(self, scheme, host, port, access_token, organization, proxy=None):
        self.url = f"{scheme}://{host}:{port}/{organization}"
        self.access_token = access_token
        self.proxy = proxy
        self._api_connection = None
        self._core_api_client = None
        self._git_api_client = None

    @staticmethod
    def create_client_from_vcs_instance(vcs_instance: VCSInstance):
        azure_devops_client = AzureDevopsConnector(
            host=vcs_instance.hostname,
            scheme=vcs_instance.scheme,
            port=vcs_instance.port,
            access_token=vcs_instance.token,
            organization=vcs_instance.organization,
        )
        return azure_devops_client

    @property
    def api_client(self):
        if not self._api_connection:
            credentials = BasicAuthentication("", self.access_token)
            connection = Connection(base_url=self.url, creds=credentials)
            self._api_connection = connection

        return self._api_connection

    @property
    def core_api_client(self):
        if not self._core_api_client:
            self._core_api_client = self.api_client.clients.get_core_client()
        return self._core_api_client

    @property
    def git_api_client(self):
        if not self._git_api_client:
            self._git_api_client = self.api_client.clients.get_git_client()
        return self._git_api_client

    def get_all_projects(self):
        try:
            self._core_api_client = self.api_client.clients.get_core_client()
            all_projects = []
            call_results: CoreClient.GetProjectsResponseValue = self.core_api_client.get_projects()
            projects = call_results.value
            all_projects.extend([project.name for project in projects])
            while call_results.continuation_token:
                call_results: CoreClient.GetProjectsResponseValue = self.core_api_client.get_projects(
                    continuation_token=call_results.continuation_token)
                projects = call_results.value
                all_projects.extend([project.name for project in projects])

            return all_projects
        except ClientRequestError as ex:
            raise ConnectionError(ex) from ex

    def project_exists(self, project_key: str) -> bool:
        return bool(self.core_api_client.get_project(project_key))

    def get_repos(self, project_key):
        return list(repo.as_dict() for repo in self.git_api_client.get_repositories(project_key))

    def get_latest_commit(self, project_key, repository_id):
        latest_commit = None
        try:
            latest_commits = list(self.git_api_client.get_commits(project=project_key, repository_id=repository_id,
                                                                  top=1, search_criteria=None))
            if latest_commits:
                latest_commit = latest_commits[0].commit_id
        except AzureDevOpsServiceError as azure_exception:
            logger.error(f"Failed to get latest commit for repository: {project_key}/{repository_id} --> "
                         f"{azure_exception}")
        return latest_commit

    @staticmethod
    def get_clone_url(clone_urls, name):
        for url in clone_urls:
            if url["name"] == name:
                return url["href"]
        return ""

    @staticmethod
    def export_repository(repository_information: Dict, latest_commit: str, vcs_instance_name: str) -> Repository:
        """
        A method which generate a repositoryInfo object about a single bitbucket repository.

        :param vcs_instance_name: Name of the VCS instance to which the repository belongs
        :param repository_information: Azure Devops repository information as returned by the Azure API.
        :param latest_commit: Azure Devops latest_commit for a single repo as returned by the Azure API.
        :return Repository object
        """
        repository = Repository(latest_commit=latest_commit,
                                vcs_instance_name=vcs_instance_name,
                                **map_azure_devops_repository(repository_information))

        return repository
