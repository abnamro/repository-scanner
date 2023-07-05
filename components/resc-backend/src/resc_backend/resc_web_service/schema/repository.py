# pylint: disable=no-name-in-module

# Third Party
from pydantic import BaseModel, HttpUrl, conint, constr


class RepositoryBase(BaseModel):
    project_key: constr(min_length=1, max_length=100)
    repository_id: constr(min_length=1, max_length=100)
    repository_name: constr(min_length=1, max_length=100)
    repository_url: HttpUrl
    vcs_instance: conint(gt=0)


class Repository(RepositoryBase):
    pass


class RepositoryCreate(RepositoryBase):
    pass


class RepositoryRead(RepositoryBase):
    id_: conint(gt=0)

    class Config:
        orm_mode = True
