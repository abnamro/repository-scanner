# pylint: disable=no-name-in-module
# Standard Library
from typing import Optional

# Third Party
from pydantic import BaseModel, conint, conlist, constr, validator

# First Party
from resc_backend.constants import AZURE_DEVOPS
from resc_backend.resc_web_service.schema.vcs_provider import VCSProviders


class VCSInstanceBase(BaseModel):

    name: constr(max_length=200)
    provider_type: VCSProviders
    hostname: constr(max_length=200)
    port: conint(gt=-0, lt=65536)
    scheme: constr(max_length=20)
    exceptions: Optional[conlist(item_type=str, min_items=None, max_items=500)]
    scope: Optional[conlist(item_type=str, min_items=None, max_items=500)]
    organization: Optional[constr(max_length=200)]

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
        try:
            if not value:
                if values["provider_type"] == AZURE_DEVOPS:
                    raise ValueError("The organization field needs to be specified for Azure devops vcs instances")
            return value
        except KeyError:
            return value

    @validator("scope", pre=True)
    @classmethod
    def check_scope_and_exceptions(cls, value, values):
        try:
            if value and values["exceptions"]:
                raise ValueError("You cannot specify bot the scope and exceptions to the scan, only one setting"
                                 " is supported.")
            return value
        except KeyError:
            return value


class VCSInstanceCreate(VCSInstanceBase):
    pass


class VCSInstanceRead(VCSInstanceBase):
    id_: conint(gt=0)

    @classmethod
    def create_from_db_vcs_instance(cls, db_vcs_instance):
        exceptions = []
        scope = []
        if db_vcs_instance.exceptions:
            exceptions = db_vcs_instance.exceptions.split(",")
        if db_vcs_instance.scope:
            scope = db_vcs_instance.scope.split(",")

        vcs_instance_read = cls(id_=db_vcs_instance.id_,
                                name=db_vcs_instance.name,
                                provider_type=db_vcs_instance.provider_type,
                                hostname=db_vcs_instance.hostname,
                                port=db_vcs_instance.port,
                                scheme=db_vcs_instance.scheme,
                                exceptions=exceptions,
                                scope=scope,
                                organization=db_vcs_instance.organization)

        return vcs_instance_read

    class Config:
        orm_mode = True
