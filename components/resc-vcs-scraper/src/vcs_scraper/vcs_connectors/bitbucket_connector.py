# Standard Library
from typing import Dict

# Third Party
import requests
from atlassian import Bitbucket

# First Party
from vcs_scraper.model import Repository
from vcs_scraper.vcs_connectors.bitbucket_data_mapper import map_bitbucket_repository
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
        try:
            return [project["key"] for project in self.api_client.project_list()]
        except (requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout, requests.exceptions.ProxyError,
                requests.exceptions.ReadTimeout, requests.exceptions.SSLError, requests.exceptions.HTTPError) as ex:
            raise ConnectionError(ex) from ex

    def project_exists(self, project_key: str) -> bool:
        return bool(self.api_client.project(project_key))

    def get_repos(self, project_key):
        return list(self.api_client.repo_all_list(project_key))

    def get_latest_commit(self, project_key, repository_id):
        last_commit = None
        latest_edited_branch = list(self.api_client.get_branches(project_key, repository_id,
                                                                 order_by="MODIFICATION", limit=1))
        if latest_edited_branch:
            last_commit = latest_edited_branch[0]["latestCommit"]
        return last_commit

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
        :param repository_information: Bitbucket repository information as returned by the Bitbucket API.
        :param latest_commit: Bitbucket latest_commit for a single repo as returned by the Bitbucket API.
        :return RepositoryInfo object
        """
        http_clone_url = BitbucketConnector.get_clone_url(repository_information["links"]["clone"], "http")
        repository = Repository(latest_commit=latest_commit,
                                repository_url=http_clone_url,
                                vcs_instance_name=vcs_instance_name,
                                **map_bitbucket_repository(repository_information))
        return repository
