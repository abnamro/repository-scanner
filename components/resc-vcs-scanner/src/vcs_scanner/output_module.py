# Standard Library
import abc
from typing import List

# Third Party
from resc_backend.resc_web_service.schema.finding import FindingCreate
from resc_backend.resc_web_service.schema.repository import Repository
from resc_backend.resc_web_service.schema.scan import Scan, ScanRead
from resc_backend.resc_web_service.schema.scan_type import ScanType

# First Party
from vcs_scanner.model import VCSInstanceRuntime


class OutputModule(metaclass=abc.ABCMeta):
    def write_vcs_instance(self, vcs_instance_runtime: VCSInstanceRuntime):
        pass

    def write_repository(self, repository: Repository):
        pass

    def write_findings(
            self,
            scan_id: int,
            repository_id: int,
            scan_findings: List[FindingCreate],):
        pass

    def write_scan(
            self,
            scan_type_to_run: ScanType,
            last_scanned_commit: str,
            scan_timestamp: str,
            repository: Repository,
            rule_pack: str) -> Scan:
        pass

    def get_last_scan_for_repository(self, repository: Repository) -> ScanRead:
        pass
