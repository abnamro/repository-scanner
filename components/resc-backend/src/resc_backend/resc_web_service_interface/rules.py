# Standard Library
import json
import logging
from typing import Optional

# Third Party
import requests
from requests import Response

# First Party
from resc_backend.constants import (
    RWS_ROUTE_DOWNLOAD_RULE_PACK,
    RWS_ROUTE_RULE_PACK,
    RWS_ROUTE_RULES,
    RWS_VERSION_PREFIX
)

logger = logging.getLogger(__name__)


def upload_rule_pack_toml_file(url: str, rule_file_path: str):
    with open(rule_file_path, "rb") as toml_file:
        files = {"rule_file": ("RESC-SECRETS-RULE.toml", toml_file, "application/octet-stream")}
        response = requests.post(url=url, files=files, proxies={"http": "", "https": ""})
        toml_file.close()
    return response


def get_newest_rule_pack_version(rws_url: str) -> Optional[str]:
    response = requests.get(url=f"{rws_url}{RWS_VERSION_PREFIX}{RWS_ROUTE_RULES}{RWS_ROUTE_RULE_PACK}")
    if response.status_code == 200:
        newest_version = json.loads(response.content)["version"]
        logger.debug(f"Latest rule pack version determined to be '{newest_version}'")
        return newest_version
    logger.error(f"Failed to determine the newest rule pack version: {response.status_code}->{response.text}")
    return None


def download_rule_pack_toml_file(rws_url: str, rule_pack_version: Optional[str] = "") -> Response:
    params = {}
    if rule_pack_version:
        params = {"rule_pack_version": rule_pack_version}
    response = requests.get(url=f"{rws_url}{RWS_VERSION_PREFIX}{RWS_ROUTE_RULES}{RWS_ROUTE_DOWNLOAD_RULE_PACK}",
                            params=params)

    if response.status_code == 200:
        logger.debug(
            f"Rule pack version: {rule_pack_version} has been successfully downloaded")
    else:
        logger.error(f"Downloading rule pack version {rule_pack_version} failed with "
                     f"error: {response.status_code}->{response.text}")
    return response
