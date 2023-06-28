# Standard Library
from typing import List

# Third Party
import requests
from github import Github
from github.Repository import Repository as GithubRepository

# First Party
from vcs_scraper.model import Repository, VCSInstance
from vcs_scraper.vcs_connectors.vcs_connector import VCSConnector


class GithubPublicConnector(VCSConnector):

    def project_exists(self, project_key: str) -> bool:
        return bool(self.api_client.get_user(project_key))

    def __init__(self, scheme, host, port, access_token, proxy=None):
        self.url = f"{scheme}://{host}:{port}"
        self.access_token = access_token
        self.proxy = proxy
        self._api_client = None

    @property
    def api_client(self):
        if not self._api_client:
            self._api_client = Github(login_or_token=self.access_token)
        return self._api_client

    def get_all_projects(self) -> List[str]:
        try:
            return [user.login for user in self.api_client.get_users()]
        except (requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout, requests.exceptions.ProxyError,
                requests.exceptions.ReadTimeout, requests.exceptions.SSLError, requests.exceptions.HTTPError) as ex:
            raise ConnectionError(ex) from ex

    def get_repos(self, project_key) -> List[dict]:
        repository_list = []
        repos = list(self.api_client.get_user(project_key).get_repos())
        for repo in repos:
            repo_details = self.get_repository_details(project_key=project_key, repository_name=repo.name)
            repo_dict = {
                "id": repo_details.id,
                "project_key": repo_details.full_name.split("/")[0],
                "name": repo_details.name,
                "html_url": repo_details.html_url
            }
            repository_list.append(repo_dict)
        return repository_list

    def get_repository_details(self, project_key: str, repository_name: str) -> GithubRepository:
        repo_details = self.api_client.get_repo(f"{project_key}/{repository_name}")
        return repo_details

    def get_latest_commit(self, project_key: str, repository_id: str) -> str:
        latest_commit = None
        self.api_client.per_page = 1
        commits = self.api_client.get_repo(f"{project_key}/{repository_id}").get_commits()
        if commits:
            latest_commit = commits[0].sha
        self.api_client.per_page = None
        return latest_commit

    @staticmethod
    def export_repository(repository_information: GithubRepository, latest_commit: str, vcs_instance_name: str) \
            -> Repository:
        """
        A method which generate a repository object about a single bitbucket repository.

        :param vcs_instance_name: Name of the VCS instance to which the repository belongs
        :param repository_information: Github repository information as returned by the Bitbucket API.
        :param latest_commit: Github latest_commit for this repo as returned by the Bitbucket API.
        :return Repository object
        """
        repository = Repository(latest_commit=latest_commit,
                                repository_url=repository_information["html_url"],
                                vcs_instance_name=vcs_instance_name,
                                repository_name=repository_information["name"],
                                repository_id=str(repository_information["id"]),
                                project_key=repository_information["project_key"])
        return repository

    @staticmethod
    def create_client_from_vcs_instance(vcs_instance: VCSInstance) -> VCSConnector:
        github_public_client = GithubPublicConnector(
            host=vcs_instance.hostname,
            scheme=vcs_instance.scheme,
            port=vcs_instance.port,
            access_token=vcs_instance.token
        )
        return github_public_client
