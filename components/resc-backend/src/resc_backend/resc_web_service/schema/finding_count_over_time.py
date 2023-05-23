# pylint: disable=no-name-in-module
# Third Party
from pydantic import BaseModel


class VcsProviderFindingCount(BaseModel):
    AZURE_DEVOPS: int = 0
    BITBUCKET: int = 0
    GITHUB_PUBLIC: int = 0


class FindingCountOverTime(BaseModel):
    time_period: str
    vcs_provider_finding_count: VcsProviderFindingCount = VcsProviderFindingCount()
    total: int = 0
