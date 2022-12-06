# Standard Library
import abc
from typing import Dict, List

# First Party
from vcs_scraper.model import Repository, VCSInstance


class VCSConnector(metaclass=abc.ABCMeta):

    @property
    @abc.abstractmethod
    def api_client(self):
        pass

    @abc.abstractmethod
    def get_all_projects(self):
        pass

    @abc.abstractmethod
    def get_repos(self, project_key):
        pass

    @abc.abstractmethod
    def get_branches(self, project_key, repository_id):
        pass

    @staticmethod
    @abc.abstractmethod
    def export_repository(repository_information: Dict, branches_information: List[Dict],
                          vcs_instance_name: str) \
            -> Repository:
        pass

    @staticmethod
    @abc.abstractmethod
    def create_client_from_vcs_instance(vcs_instance: VCSInstance):
        pass

    @abc.abstractmethod
    def project_exists(self, project_key: str) -> bool:
        pass
