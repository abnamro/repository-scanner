# Standard Library
from enum import Enum

# First Party
from resc_backend.constants import AZURE_DEVOPS, BITBUCKET, GITHUB_PUBLIC


class VCSProviders(str, Enum):
    AZURE_DEVOPS = AZURE_DEVOPS
    BITBUCKET = BITBUCKET
    GITHUB_PUBLIC = GITHUB_PUBLIC
