# pylint: disable=no-name-in-module
# Standard Library
import datetime

# Third Party
from pydantic import BaseModel, HttpUrl, conint, constr

# First Party
from resc_backend.resc_web_service.schema.vcs_provider import VCSProviders


class RepositoryEnrichedBase(BaseModel):
    project_key: constr(min_length=1, max_length=100)
    repository_id: constr(min_length=1, max_length=100)
    repository_name: constr(min_length=1, max_length=100)
    repository_url: HttpUrl
    vcs_provider: VCSProviders
    last_scan_id: conint(gt=0) = None
    last_scan_timestamp: datetime.datetime = None
    true_positive: conint(gt=-1)
    false_positive: conint(gt=-1)
    not_analyzed: conint(gt=-1)
    under_review: conint(gt=-1)
    clarification_required: conint(gt=-1)
    total_findings_count: conint(gt=-1)


class RepositoryEnriched(RepositoryEnrichedBase):
    pass


class RepositoryEnrichedRead(RepositoryEnriched):
    id_: conint(gt=0)

    class Config:
        orm_mode = True
