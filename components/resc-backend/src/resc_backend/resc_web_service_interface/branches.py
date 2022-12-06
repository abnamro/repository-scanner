# Standard Library
import logging

# Third Party
import requests

# First Party
from resc_backend.constants import RWS_ROUTE_BRANCHES, RWS_ROUTE_LAST_SCAN, RWS_VERSION_PREFIX
from resc_backend.resc_web_service.schema.branch import BranchCreate

logger = logging.getLogger(__name__)


def create_branch(url: str, branch: BranchCreate):
    api_url = f"{url}{RWS_VERSION_PREFIX}{RWS_ROUTE_BRANCHES}"
    response = requests.post(api_url, data=branch.json(), proxies={"http": "", "https": ""})
    return response


def get_last_scan_for_branch(url: str, branch_id: int):
    api_url = f"{url}{RWS_VERSION_PREFIX}{RWS_ROUTE_BRANCHES}/{branch_id}{RWS_ROUTE_LAST_SCAN}"
    response = requests.get(api_url, proxies={"http": "", "https": ""})
    return response
