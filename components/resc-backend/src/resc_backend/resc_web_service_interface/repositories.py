# Standard Library
import logging

# Third Party
import requests

# First Party
from resc_backend.constants import RWS_ROUTE_REPOSITORIES, RWS_VERSION_PREFIX
from resc_backend.resc_web_service.schema.repository import Repository

logger = logging.getLogger(__name__)


def create_repository(url: str, repository: Repository):
    api_url = f"{url}{RWS_VERSION_PREFIX}{RWS_ROUTE_REPOSITORIES}"
    response = requests.post(api_url, data=repository.json(), proxies={"http": "", "https": ""})
    return response
