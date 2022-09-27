# pylint: disable=W0212
# Standard Library
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Third Party
from repository_scanner_backend.constants import TEMP_RULE_FILE
from repository_scanner_backend.resc_web_service.schema.branch_info import BranchInfoCreate, BranchInfoRead
from repository_scanner_backend.resc_web_service.schema.finding import FindingBase, FindingCreate
from repository_scanner_backend.resc_web_service.schema.repository_info import RepositoryInfoCreate, RepositoryInfoRead
from repository_scanner_backend.resc_web_service.schema.scan import Scan, ScanCreate, ScanRead
from repository_scanner_backend.resc_web_service.schema.scan_type import ScanType
from repository_scanner_backend.resc_web_service.schema.vcs_instance import VCSInstanceCreate, VCSInstanceRead
from repository_scanner_backend.resc_web_service_interface.branches_info import (
    create_branch_info,
    get_last_scan_for_branch
)
from repository_scanner_backend.resc_web_service_interface.findings import create_findings_with_scan_id
from repository_scanner_backend.resc_web_service_interface.repositories_info import create_repository_info
from repository_scanner_backend.resc_web_service_interface.rules import download_rule_pack_toml_file
from repository_scanner_backend.resc_web_service_interface.scans import create_scan
from repository_scanner_backend.resc_web_service_interface.vcs_instances import create_vcs_instance
from tenacity import retry, stop_after_attempt, wait_exponential

# First Party
from repository_scanners.common import get_rule_pack_version_from_file
from repository_scanners.model import VCSInstanceRuntime
from repository_scanners.output_module import OutputModule

logger = logging.getLogger(__name__)


class RESTAPIWriter(OutputModule):

    def __init__(self, rws_url):
        self.rws_url = rws_url

    def write_vcs_instance(self, vcs_instance_runtime: VCSInstanceRuntime) -> Optional[VCSInstanceRead]:
        created_vcs_instance = None
        vcs_instance = VCSInstanceCreate(name=vcs_instance_runtime.name,
                                         provider_type=vcs_instance_runtime.provider_type,
                                         hostname=vcs_instance_runtime.hostname,
                                         port=vcs_instance_runtime.port,
                                         scheme=vcs_instance_runtime.scheme,
                                         exceptions=vcs_instance_runtime.exceptions,
                                         scope=vcs_instance_runtime.scope,
                                         organization=vcs_instance_runtime.organization)
        response = create_vcs_instance(self.rws_url, vcs_instance)
        if response.status_code == 201:
            created_vcs_instance = VCSInstanceRead(**json.loads(response.text))
        else:
            logger.warning(f"Creating vcs_instance failed with error: {response.status_code}->{response.text}")
        return created_vcs_instance

    def write_repository_info(self, repository_info: RepositoryInfoCreate) -> Optional[RepositoryInfoRead]:
        created_repository_info = None
        response = create_repository_info(self.rws_url,
                                          repository_info)
        if response.status_code == 201:
            created_repository_info = RepositoryInfoRead(**json.loads(response.text))
        else:
            logger.warning(f"Creating repository info failed with error: {response.status_code}->{response.text}")
        return created_repository_info

    def write_branch_info(self, repository_info: RepositoryInfoRead, branch: BranchInfoCreate) \
            -> Optional[BranchInfoRead]:
        created_branch_info = None
        branch_info = BranchInfoCreate.create_from_base_class(
            base_object=branch, repository_info_id=repository_info.id_)

        response = create_branch_info(self.rws_url, branch_info)
        if response.status_code == 201:
            created_branch_info = BranchInfoRead(**json.loads(response.text))
        else:
            logger.warning(f"Creating branch info failed with error: {response.status_code}->{response.text}")
        return created_branch_info

    def write_findings(
            self,
            scan_id: int,
            branch_info_id: int,
            scan_findings: List[FindingBase], ):
        findings_create = []
        for finding in scan_findings:
            new_finding = FindingCreate.create_from_base_class(base_object=finding, branch_info_id=branch_info_id)
            findings_create.append(new_finding)

        response = create_findings_with_scan_id(self.rws_url,
                                                findings_create,
                                                scan_id)

        if response.status_code != 201:
            logger.warning(f"Creating findings for scan {scan_id} "
                           f"failed with error: {response.status_code}->{response.text}")
        logger.info(f"Found {len(scan_findings)} issues during scan: {scan_id} ")

    def write_scan(
            self,
            scan_type_to_run: ScanType,
            last_scanned_commit: str,
            scan_timestamp: datetime,
            branch_info: BranchInfoRead,
            rule_pack: str) -> ScanRead:
        created_scan = None
        scan_object = ScanCreate.create_from_base_class(
            base_object=Scan(scan_type=scan_type_to_run, last_scanned_commit=last_scanned_commit,
                             timestamp=scan_timestamp, rule_pack=rule_pack), branch_info_id=branch_info.id_)

        response = create_scan(self.rws_url, scan_object)
        if response.status_code == 201:
            created_scan = ScanRead(**json.loads(response.text))
            logger.info(f"Successfully created scan for branch {branch_info.branch_name} ")
        else:
            logger.warning(
                f"Creating {scan_type_to_run} scan failed with error: {response.status_code}->{response.text}")

        return created_scan

    def get_last_scanned_commit(self, branch_info: BranchInfoRead):
        last_scanned_commit = None
        response = get_last_scan_for_branch(self.rws_url,
                                            branch_info.id_)
        if response.status_code == 200:
            json_body = json.loads(response.text)
            last_scanned_commit = json_body['last_scanned_commit'] if json_body else None
        else:
            logger.warning(f"Retrieving last scan details failed with error: {response.status_code}->{response.text}")
        return last_scanned_commit

    def download_rule_pack(self, rule_pack_version: Optional[str] = "") -> str:
        response = download_rule_pack_toml_file(self.rws_url, rule_pack_version)
        if response.status_code == 200:
            filename = Path(TEMP_RULE_FILE)
            filename.write_bytes(response.content)
            logger.debug(
                f"Rule pack version: {rule_pack_version} has been successfully downloaded to location {TEMP_RULE_FILE}")
            if not rule_pack_version:
                rule_pack_version = get_rule_pack_version_from_file(response.content)
                if not rule_pack_version:
                    logger.warning("Unable to obtain the rule pack version from downloaded file, defaulting to '0.0.0'")
            return rule_pack_version

        logger.error(f"Aborting scan! Downloading rule pack version {rule_pack_version} failed with "
                     f"error: {response.status_code}->{response.text}")
        sys.exit(-1)

    @retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(100))
    def write_vcs_instances(self, vcs_instances_dict: Dict[str, VCSInstanceRuntime]) \
            -> Dict[str, VCSInstanceRuntime]:
        try:
            for key in vcs_instances_dict:
                vcs_instance = vcs_instances_dict[key]
                vcs_instance_created = self.write_vcs_instance(vcs_instance)
                if not vcs_instance_created:
                    raise ValueError(f"Failed creating vcs instance {vcs_instance.name}")
                vcs_instance.id_ = vcs_instance_created.id_
                vcs_instances_dict[key] = vcs_instance
            return vcs_instances_dict
        except ValueError as ex:
            logger.error(f"Failed creating vcs instances, is the API available? | {ex} | Retrying...")
            raise
