# Standard Library
import logging
import os
from typing import Dict, List

# Third Party
from azure.devops.connection import Connection
from azure.devops.exceptions import AzureDevOpsServiceError
from azure.devops.released.core.core_client import CoreClient
from msrest.authentication import BasicAuthentication

# First Party
from vcs_scraper.model import BranchInfo, RepositoryInfo
from vcs_scraper.vcs_connectors.azure_devops_data_mapper import (
    map_azure_devops_branch_info,
    map_azure_devops_repository_info
)
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

    def project_exists(self, project_key: str) -> bool:
        return bool(self.core_api_client.get_project(project_key))

    def get_repos(self, project_key):
        return list(repo.as_dict() for repo in self.git_api_client.get_repositories(project_key))

    def get_branches(self, project_key, repository_id):
        all_branches = []
        try:
            all_branches = list(self.git_api_client.get_branches(project=project_key, repository_id=repository_id))
            all_branches = [branch.as_dict() for branch in all_branches]
        except AzureDevOpsServiceError as azure_exception:
            logger.error(f"Failed to list branches for repository: {project_key}/{repository_id} --> {azure_exception}")
        return all_branches

    @staticmethod
    def get_clone_url(clone_urls, name):
        for url in clone_urls:
            if url["name"] == name:
                return url["href"]
        return ""

    @staticmethod
    def export_repository_info(repository_information: Dict, branches_information: List[Dict],
                               vcs_instance_name: str) \
            -> RepositoryInfo:
        """
        A method which generate a repositoryInfo object about a single bitbucket repository.

        :param vcs_instance_name: Name of the VCS instance to which the repository belongs
        :param repository_information: Azure Devops repository information as returned by the Azure API.
        :param branches_information: Azure Devops branches information for a single repo as returned by the Azure API.
        :return RepositoryInfo object
        """

        branches: List[BranchInfo] = []
        for branch_information in branches_information:
            if os.getenv('SCAN_ONLY_MASTER_BRANCH', "true").lower() in "true":
                if branch_information["name"].lower() in ["main", "master"]:
                    branch_info = BranchInfo(repository_info_id=repository_information["id"],
                                             **map_azure_devops_branch_info(branch_information))
                    branches.append(branch_info)
                    break
            else:
                branch_info = BranchInfo(repository_info_id=repository_information["id"],
                                         **map_azure_devops_branch_info(branch_information))
                branches.append(branch_info)

        repository_info = RepositoryInfo(branches_info=branches,
                                         vcs_instance_name=vcs_instance_name,
                                         **map_azure_devops_repository_info(repository_information))

        return repository_info
