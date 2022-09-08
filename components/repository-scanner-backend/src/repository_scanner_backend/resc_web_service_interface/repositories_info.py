# Standard Library
import logging

# Third Party
import requests

# First Party
from repository_scanner_backend.constants import RWS_ROUTE_REPOSITORIES_INFO, RWS_VERSION_PREFIX
from repository_scanner_backend.resc_web_service.schema.repository_info import RepositoryInfo

logger = logging.getLogger(__name__)


def create_repository_info(url: str, repository_info: RepositoryInfo):
    api_url = f"{url}{RWS_VERSION_PREFIX}{RWS_ROUTE_REPOSITORIES_INFO}"
    response = requests.post(api_url, data=repository_info.json(), proxies={"http": "", "https": ""})
    return response
