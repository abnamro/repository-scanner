# Standard Library
import abc
from typing import List

# Third Party
from resc_backend.resc_web_service.schema.branch_info import BranchInfo
from resc_backend.resc_web_service.schema.finding import FindingCreate
from resc_backend.resc_web_service.schema.repository_info import RepositoryInfo
from resc_backend.resc_web_service.schema.scan import Scan
from resc_backend.resc_web_service.schema.scan_type import ScanType

# First Party
from repository_scanners.model import VCSInstanceRuntime


class OutputModule(metaclass=abc.ABCMeta):
    def write_vcs_instance(self, vcs_instance_runtime: VCSInstanceRuntime):
        pass

    def write_repository_info(self, repository_info: RepositoryInfo):
        pass

    def write_branch_info(self, repository_info: RepositoryInfo, branch: BranchInfo):
        pass

    def write_findings(
            self,
            scan_id: int,
            branch_info_id: int,
            scan_findings: List[FindingCreate],):
        pass

    def write_scan(
            self,
            scan_type_to_run: ScanType,
            last_scanned_commit: str,
            scan_timestamp: str,
            branch_info: BranchInfo,
            rule_pack: str) -> Scan:
        pass

    def get_last_scanned_commit(self, branch_info: BranchInfo):
        pass
