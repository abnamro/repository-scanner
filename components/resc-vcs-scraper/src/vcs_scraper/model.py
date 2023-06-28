# pylint: disable=no-name-in-module
# Standard Library
import dataclasses
import json
import os
from enum import Enum
from typing import List, Optional

# Third Party
from pydantic import BaseModel, validator
from pydantic.types import conint, constr

# First Party
from vcs_scraper.constants import AZURE_DEVOPS, BITBUCKET, GITHUB_PUBLIC


@dataclasses.dataclass
class Repository:

    repository_name: str
    repository_id: str
    repository_url: str
    project_key: str
    vcs_instance_name: str
    latest_commit: str

    def json(self):
        json_repo = json.dumps(dataclasses.asdict(self))
        return json_repo


class VCSProviders(str, Enum):
    AZURE_DEVOPS = AZURE_DEVOPS
    BITBUCKET = BITBUCKET
    GITHUB_PUBLIC = GITHUB_PUBLIC


class VCSInstance(BaseModel):

    name: constr(max_length=200)
    provider_type: VCSProviders
    hostname: constr(max_length=200)
    port: conint(gt=-0, lt=65536)
    scheme: str
    username: constr(max_length=200)
    token: constr(max_length=200)
    exceptions: Optional[List[str]] = []
    scope: Optional[List[str]] = []
    organization: Optional[str]

    @validator("scheme", pre=True)
    @classmethod
    def check_scheme(cls, value):
        allowed_schemes = ["http", "https"]
        if value not in allowed_schemes:
            raise ValueError(f"The scheme '{value}' must be one of the following {', '.join(allowed_schemes)}")
        return value

    @validator("organization", pre=True)
    @classmethod
    def check_organization(cls, value, values):
        if not value:
            if values["provider_type"] == AZURE_DEVOPS:
                raise ValueError("The organization field needs to be specified for Azure devops vcs instances")
        return value

    @validator("scope", pre=True)
    @classmethod
    def check_scope_and_exceptions(cls, value, values):
        if value and values["exceptions"]:
            raise ValueError("You cannot specify bot the scope and exceptions to the scan, only one setting"
                             " is supported.")
        return value

    @validator("username", pre=True)
    @classmethod
    def check_presence_of_username(cls, value, values):
        if not os.environ.get(value):
            raise ValueError(f"The username for VCS Instance {values['name']} could not be found in the "
                             f"environment variable {value}")
        return os.environ.get(value)

    @validator("token", pre=True)
    @classmethod
    def check_presence_of_token(cls, value, values):
        if not os.environ.get(value):
            raise ValueError(f"The access token for VCS Instance {values['name']} could not be found in the "
                             f"environment variable {value}")
        return os.environ.get(value)
