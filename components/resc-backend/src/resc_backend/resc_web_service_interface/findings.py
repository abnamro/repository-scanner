# Standard Library
import json
import logging
from typing import List

# Third Party
import requests

# First Party
from resc_backend.constants import RWS_ROUTE_FINDINGS, RWS_ROUTE_SCANS, RWS_VERSION_PREFIX
from resc_backend.resc_web_service.schema.finding import FindingCreate

logger = logging.getLogger(__name__)


def create_findings(url: str, findings: List[FindingCreate]) -> requests.Response:
    api_url = f"{url}{RWS_VERSION_PREFIX}{RWS_ROUTE_FINDINGS}"

    findings_json = []
    for finding in findings:
        findings_json.append(json.loads(finding.json()))

    response = requests.post(api_url, json=findings_json, proxies={"http": "", "https": ""})
    return response


def create_findings_with_scan_id(url: str, findings: List[FindingCreate], scan_id: int) -> requests.Response:
    api_url = f"{url}{RWS_VERSION_PREFIX}{RWS_ROUTE_SCANS}/{scan_id}{RWS_ROUTE_FINDINGS}"

    findings_json = []
    for finding in findings:
        findings_json.append(json.loads(finding.json()))

    response = requests.post(api_url, json=findings_json, proxies={"http": "", "https": ""})
    return response
