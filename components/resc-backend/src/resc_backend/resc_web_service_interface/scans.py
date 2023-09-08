# Standard Library
import logging

# Third Party
import requests

# First Party
from resc_backend.constants import RWS_ROUTE_SCANS, RWS_VERSION_PREFIX
from resc_backend.resc_web_service.schema.scan import ScanCreate

logger = logging.getLogger(__name__)


def create_scan(url: str, scan: ScanCreate):
    api_url = f"{url}{RWS_VERSION_PREFIX}{RWS_ROUTE_SCANS}"
    response = requests.post(api_url, data=scan.json(), proxies={"http": "", "https": ""}, timeout=10)
    return response
