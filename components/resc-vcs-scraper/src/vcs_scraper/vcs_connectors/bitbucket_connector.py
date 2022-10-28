# Standard Library
import os
from typing import Dict, List

# Third Party
import requests
from atlassian import Bitbucket

# First Party
from vcs_scraper.model import Branch, Repository
from vcs_scraper.vcs_connectors.bitbucket_data_mapper import map_bitbucket_branch, map_bitbucket_repository
from vcs_scraper.vcs_connectors.vcs_connector import VCSConnector
from vcs_scraper.vcs_instances_parser import VCSInstance


class BitbucketConnector(VCSConnector):
    def __init__(self, scheme, host, port, access_token, proxy=None):
        self.url = f"{scheme}://{host}:{port}"
        self.access_token = access_token
        self.proxy = proxy
        self._api_client = None

    @staticmethod
    def create_client_from_vcs_instance(vcs_instance: VCSInstance):
        bitbucket_client = BitbucketConnector(
            host=vcs_instance.hostname,
            scheme=vcs_instance.scheme,
            port=vcs_instance.port,
            access_token=vcs_instance.token
        )
        return bitbucket_client

    @property
    def api_client(self):
        if not self._api_client:
            session = requests.Session()
            session.headers['Authorization'] = f"Bearer {self.access_token}"
            self._api_client = Bitbucket(
                url=self.url,
                session=session,
                proxies={"no_proxy": self.proxy}
            )
        return self._api_client

    def get_all_projects(self):
        return [project["key"] for project in self.api_client.project_list()]

    def project_exists(self, project_key: str) -> bool:
        return bool(self.api_client.project(project_key))

    def get_repos(self, project_key):
        return list(self.api_client.repo_all_list(project_key))

    def get_branches(self, project_key, repository_id):
        return list(self.api_client.get_branches(project_key, repository_id))

    @staticmethod
    def get_clone_url(clone_urls, name):
        for url in clone_urls:
            if url["name"] == name:
                return url["href"]
        return ""

    @staticmethod
    def export_repository(repository_information: Dict, branches_information: List[Dict],
                          vcs_instance_name: str) \
            -> Repository:
        """
        A method which generate a repositoryInfo object about a single bitbucket repository.

        :param vcs_instance_name: Name of the VCS instance to which the repository belongs
        :param repository_information: Bitbucket repository information as returned by the Bitbucket API.
        :param branches_information: Bitbucket branches information for a single repo as returned by the Bitbucket API.
        :return RepositoryInfo object
        """

        branches: List[Branch] = []
        for branch_information in branches_information:
            if os.getenv('SCAN_ONLY_MASTER_BRANCH', "true").lower() in "true":
                if branch_information["displayId"].lower() in ["main", "master"]:
                    branch = Branch(repository_id=repository_information["id"],
                                    **map_bitbucket_branch(branch_information))
                    branches.append(branch)
                    break
            else:
                branch = Branch(repository_id=repository_information["id"],
                                **map_bitbucket_branch(branch_information))
                branches.append(branch)
        http_clone_url = BitbucketConnector.get_clone_url(repository_information["links"]["clone"], "http")
        repository = Repository(branches=branches,
                                repository_url=http_clone_url,
                                vcs_instance_name=vcs_instance_name,
                                **map_bitbucket_repository(repository_information))
        return repository
