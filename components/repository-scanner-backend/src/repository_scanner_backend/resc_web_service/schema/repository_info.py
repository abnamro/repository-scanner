# pylint: disable=no-name-in-module
# Third Party
from pydantic import BaseModel, HttpUrl, conint, constr
from pydantic.types import List

# First Party
from repository_scanner_backend.resc_web_service.schema.branch_info import BranchInfo


class RepositoryInfoBase(BaseModel):
    project_key: constr(min_length=1, max_length=100)
    repository_id: constr(min_length=1, max_length=100)
    repository_name: constr(min_length=1, max_length=100)
    repository_url: HttpUrl
    vcs_instance: conint(gt=0)


class RepositoryInfo(RepositoryInfoBase):
    branches_info: List[BranchInfo]


class RepositoryInfoCreate(RepositoryInfoBase):
    pass


class RepositoryInfoRead(RepositoryInfoBase):
    id_: conint(gt=0)

    class Config:
        orm_mode = True
