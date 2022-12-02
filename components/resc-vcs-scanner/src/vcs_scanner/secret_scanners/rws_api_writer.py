# pylint: disable=W0212
# Standard Library
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Third Party
from resc_backend.constants import TEMP_RULE_FILE
from resc_backend.resc_web_service.schema.branch import BranchCreate, BranchRead
from resc_backend.resc_web_service.schema.finding import FindingBase, FindingCreate
from resc_backend.resc_web_service.schema.repository import RepositoryCreate, RepositoryRead
from resc_backend.resc_web_service.schema.scan import Scan, ScanCreate, ScanRead
from resc_backend.resc_web_service.schema.scan_type import ScanType
from resc_backend.resc_web_service.schema.vcs_instance import VCSInstanceCreate, VCSInstanceRead
from resc_backend.resc_web_service_interface.branches import create_branch, get_last_scan_for_branch
from resc_backend.resc_web_service_interface.findings import create_findings_with_scan_id
from resc_backend.resc_web_service_interface.repositories import create_repository
from resc_backend.resc_web_service_interface.rule_packs import download_rule_pack_toml_file
from resc_backend.resc_web_service_interface.scans import create_scan
from resc_backend.resc_web_service_interface.vcs_instances import create_vcs_instance
from tenacity import retry, stop_after_attempt, wait_exponential

# First Party
from vcs_scanner.common import get_rule_pack_version_from_file
from vcs_scanner.model import VCSInstanceRuntime
from vcs_scanner.output_module import OutputModule

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

    def write_repository(self, repository: RepositoryCreate) -> Optional[RepositoryRead]:
        created_repository = None
        response = create_repository(self.rws_url,
                                     repository)
        if response.status_code == 201:
            created_repository = RepositoryRead(**json.loads(response.text))
        else:
            logger.warning(f"Creating repository failed with error: {response.status_code}->{response.text}")
        return created_repository

    def write_branch(self, repository: RepositoryRead, branch: BranchCreate) \
            -> Optional[BranchRead]:
        created_branch = None
        branch = BranchCreate.create_from_base_class(
            base_object=branch, repository_id=repository.id_)

        response = create_branch(self.rws_url, branch)
        if response.status_code == 201:
            created_branch = BranchRead(**json.loads(response.text))
        else:
            logger.warning(f"Creating branch failed with error: {response.status_code}->{response.text}")
        return created_branch

    def write_findings(
            self,
            scan_id: int,
            branch_id: int,
            scan_findings: List[FindingBase], ):
        findings_create = []
        for finding in scan_findings:
            new_finding = FindingCreate.create_from_base_class(base_object=finding, branch_id=branch_id)
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
            branch: BranchRead,
            rule_pack: str) -> ScanRead:
        created_scan = None
        scan_object = ScanCreate.create_from_base_class(
            base_object=Scan(scan_type=scan_type_to_run, last_scanned_commit=last_scanned_commit,
                             timestamp=scan_timestamp, rule_pack=rule_pack), branch_id=branch.id_)

        response = create_scan(self.rws_url, scan_object)
        if response.status_code == 201:
            created_scan = ScanRead(**json.loads(response.text))
            logger.info(f"Successfully created scan for branch {branch.branch_name} ")
        else:
            logger.warning(
                f"Creating {scan_type_to_run} scan failed with error: {response.status_code}->{response.text}")

        return created_scan

    def get_last_scanned_commit(self, branch: BranchRead):
        last_scanned_commit = None
        response = get_last_scan_for_branch(self.rws_url,
                                            branch.id_)
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
            if rule_pack_version:
                logger.debug(
                    f"Rule pack version: {rule_pack_version} has been successfully "
                    f"downloaded to location {TEMP_RULE_FILE}")
            else:
                rule_pack_version = get_rule_pack_version_from_file(response.content)
                if not rule_pack_version:
                    logger.warning("Unable to obtain the rule pack version from downloaded file, defaulting to '0.0.0'")
                logger.debug(
                    f"Latest rule pack version: {rule_pack_version} has been successfully "
                    f"downloaded to location {TEMP_RULE_FILE}")
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
