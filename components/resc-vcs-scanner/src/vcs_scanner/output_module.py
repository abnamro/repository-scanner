# Standard Library
import abc
from typing import List

# Third Party
from resc_backend.resc_web_service.schema.branch import Branch
from resc_backend.resc_web_service.schema.finding import FindingCreate
from resc_backend.resc_web_service.schema.repository import Repository
from resc_backend.resc_web_service.schema.scan import Scan
from resc_backend.resc_web_service.schema.scan_type import ScanType

# First Party
from vcs_scanner.model import VCSInstanceRuntime


class OutputModule(metaclass=abc.ABCMeta):
    def write_vcs_instance(self, vcs_instance_runtime: VCSInstanceRuntime):
        pass

    def write_repository(self, repository: Repository):
        pass

    def write_branch(self, repository: Repository, branch: Branch):
        pass

    def write_findings(
            self,
            scan_id: int,
            branch_id: int,
            scan_findings: List[FindingCreate],):
        pass

    def write_scan(
            self,
            scan_type_to_run: ScanType,
            last_scanned_commit: str,
            scan_timestamp: str,
            branch: Branch,
            rule_pack: str) -> Scan:
        pass

    def get_last_scanned_commit(self, branch: Branch):
        pass
