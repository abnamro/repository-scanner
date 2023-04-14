# pylint: disable=no-name-in-module
# pylint: disable=E0213

# Standard Library
import datetime
from typing import Dict, Optional

# Third Party
from pydantic import BaseModel, HttpUrl, conint, constr, root_validator

# First Party
from resc_backend.resc_web_service.schema.finding_status import FindingStatus
from resc_backend.resc_web_service.schema.vcs_provider import VCSProviders


class DetailedFindingBase(BaseModel):
    file_path: str
    line_number: conint(gt=-1)
    column_start: conint(gt=-1)
    column_end: conint(gt=-1)
    commit_id: constr(max_length=120)
    commit_message: str
    commit_timestamp: datetime.datetime
    author: constr(max_length=200)
    email: constr(max_length=100)
    status: Optional[FindingStatus] = FindingStatus.NOT_ANALYZED
    comment: Optional[constr(max_length=255)] = None
    rule_name: constr(max_length=200)
    rule_pack: constr(max_length=100)
    project_key: constr(min_length=1, max_length=100)
    repository_name: constr(min_length=1, max_length=100)
    repository_url: HttpUrl
    timestamp: datetime.datetime
    vcs_provider: VCSProviders
    branch_name: constr(min_length=1, max_length=200)
    last_scanned_commit: constr(min_length=1, max_length=100)
    scan_id: conint(gt=0)
    event_sent_on: Optional[datetime.datetime]


class DetailedFinding(DetailedFindingBase):
    pass


class DetailedFindingRead(DetailedFinding):
    id_: conint(gt=0)
    commit_url: Optional[constr(min_length=1)]

    @staticmethod
    def build_bitbucket_commit_url(repository_url: str,
                                   repository_name: str,
                                   project_key: str,
                                   file_path: str,
                                   commit_id: str) -> str:

        arr = repository_url.split('/')
        if len(arr) >= 3:
            repo_base_url = arr[0] + '//' + arr[2]
        else:
            repo_base_url = repository_url
        bitbucket_commit_url = f"{repo_base_url}/projects/{project_key}/repos/" \
                               f"{repository_name}/browse/{file_path}?at={commit_id}"
        commit_url = bitbucket_commit_url
        return commit_url

    @staticmethod
    def build_ado_commit_url(repository_url: str,
                             branch_name: str,
                             file_path: str,
                             commit_id: str) -> str:
        ado_commit_url = f"{repository_url}/commit/{commit_id}?" \
                         f"refName=refs/heads/{branch_name}&path=/{file_path}"
        return ado_commit_url

    @staticmethod
    def build_github_commit_url(repository_url: str,
                                branch_name: str,
                                file_path: str,
                                commit_id: str) -> str:
        github_commit_url = f"{repository_url}/commit/{commit_id}?" \
                            f"refName=refs/heads/{branch_name}&path=/{file_path}"
        return github_commit_url

    @root_validator
    def build_commit_url(cls, values) -> Dict:
        if values["status"] is None:
            values["status"] = FindingStatus.NOT_ANALYZED
        if values["comment"] is None:
            values["comment"] = ""
        if values["vcs_provider"] == VCSProviders.BITBUCKET:
            values["commit_url"] = cls.build_bitbucket_commit_url(repository_url=values["repository_url"],
                                                                  repository_name=values["repository_name"],
                                                                  project_key=values["project_key"],
                                                                  file_path=values["file_path"],
                                                                  commit_id=values["commit_id"])
        elif values["vcs_provider"] == VCSProviders.AZURE_DEVOPS:
            values["commit_url"] = cls.build_ado_commit_url(repository_url=values["repository_url"],
                                                            branch_name=values["branch_name"],
                                                            file_path=values["file_path"],
                                                            commit_id=values["commit_id"])

        elif values["vcs_provider"] == VCSProviders.GITHUB_PUBLIC:
            values["commit_url"] = cls.build_github_commit_url(repository_url=values["repository_url"],
                                                               branch_name=values["branch_name"],
                                                               file_path=values["file_path"],
                                                               commit_id=values["commit_id"])
        else:
            raise Exception(f"Unsupported VCSProvider: {values['vcs_provider']}")
        return values

    class Config:
        orm_mode = True
