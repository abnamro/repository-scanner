# Standard Library
import logging

# Third Party
import requests

# First Party
from repository_scanner_backend.constants import RWS_ROUTE_BRANCHES_INFO, RWS_ROUTE_LAST_SCAN, RWS_VERSION_PREFIX
from repository_scanner_backend.resc_web_service.schema.branch_info import BranchInfoCreate

logger = logging.getLogger(__name__)


def create_branch_info(url: str, branch_info: BranchInfoCreate):
    api_url = f"{url}{RWS_VERSION_PREFIX}{RWS_ROUTE_BRANCHES_INFO}"
    response = requests.post(api_url, data=branch_info.json(), proxies={"http": "", "https": ""})
    return response


def get_last_scan_for_branch(url: str, branch_info_id: int):
    api_url = f"{url}{RWS_VERSION_PREFIX}{RWS_ROUTE_BRANCHES_INFO}/{branch_info_id}{RWS_ROUTE_LAST_SCAN}"
    response = requests.get(api_url, proxies={"http": "", "https": ""})
    return response
