# Standard Library
import logging

# Third Party
import requests

# First Party
from repository_scanner_backend.constants import RWS_ROUTE_VCS, RWS_VERSION_PREFIX
from repository_scanner_backend.resc_web_service.schema.vcs_instance import VCSInstanceCreate

logger = logging.getLogger(__name__)


def create_vcs_instance(url: str, vcs_instance: VCSInstanceCreate):
    api_url = f"{url}{RWS_VERSION_PREFIX}{RWS_ROUTE_VCS}"
    response = requests.post(api_url, data=vcs_instance.json(), proxies={"http": "", "https": ""})
    return response
