# pylint: disable=wrong-import-position
# Standard Library
import logging

# Third Party
import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry

# First Party
from resc_backend.constants import RWS_ROUTE_HEALTH, RWS_VERSION_PREFIX

logger = logging.getLogger()


def wait_for_api_to_up(api_base_url: str):
    """
        This function returns true once the STS API is up.
    :param api_base_url:
        API base url
    :return: True/False
        Returns True if API server is up else returns False
    """

    session = requests.Session()
    retries = Retry(total=100,
                    backoff_factor=1,
                    status_forcelist=[404, 500, 502, 503, 504])
    uri = f"{api_base_url}{RWS_VERSION_PREFIX}{RWS_ROUTE_HEALTH}"
    session.mount("http://", HTTPAdapter(max_retries=retries))
    response = session.get(uri)

    if hasattr(response, "status_code") and int(response.status_code) == 200:
        logger.debug("API server is up")
        return True
    logger.error(f"API is down, HTTP status: '{response.status_code}'")
    return False
