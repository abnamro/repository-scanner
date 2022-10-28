# Standard Library
import logging
from datetime import datetime
from typing import List, Optional

# Third Party
from resc_backend.resc_web_service.schema.branch import Branch
from resc_backend.resc_web_service.schema.finding import FindingCreate
from resc_backend.resc_web_service.schema.repository import Repository
from resc_backend.resc_web_service.schema.scan import ScanRead
from resc_backend.resc_web_service.schema.scan_type import ScanType
from resc_backend.resc_web_service.schema.vcs_instance import VCSInstanceRead

# First Party
from vcs_scanner.model import VCSInstanceRuntime
from vcs_scanner.output_module import OutputModule

logger = logging.getLogger(__name__)


class STDOUTWriter(OutputModule):
    def write_vcs_instance(self, vcs_instance_runtime: VCSInstanceRuntime) -> Optional[VCSInstanceRead]:
        vcs_instance = VCSInstanceRead(id_=1,
                                       name=vcs_instance_runtime.name,
                                       provider_type=vcs_instance_runtime.provider_type,
                                       hostname=vcs_instance_runtime.hostname,
                                       port=vcs_instance_runtime.port,
                                       scheme=vcs_instance_runtime.scheme,
                                       exceptions=vcs_instance_runtime.exceptions,
                                       scope=vcs_instance_runtime.scope,
                                       organization=vcs_instance_runtime.organization)
        logger.info(f"Scanning vcs instance {vcs_instance.name}")
        return vcs_instance

    def write_repository(self, repository: Repository) -> Repository:
        logger.info(f"Scanning repository {repository.project_key}/{repository.repository_name}")
        return repository

    def write_branch(self, repository: Repository, branch: Branch) -> Optional[Branch]:
        logger.info(f"Scanning branch {branch.branch_name} of repository {repository.repository_name}")
        return branch

    @staticmethod
    def format_commit_message(finding: FindingCreate) -> str:
        commit_message = (finding.commit_message[:40] + '..') \
            if len(finding.commit_message) > 40 else finding.commit_message
        return (f"Finding details:\n"
                f"  -Filepath:        {finding.file_path}\n"
                f"  -Line number:     {finding.line_number}\n"
                f"  -Rule name:       {finding.rule_name}\n"
                "Commit details:\n"
                f"  -Commit ID:       {finding.commit_id}\n"
                f"  -Commit Message:  {commit_message}\n"
                f"  -Commit time:     {finding.commit_timestamp}\n"
                "Author details:\n"
                f"  -Author name:     {finding.author}\n"
                f"  -Author email:    {finding.email}\n")

    def write_findings(
            self,
            scan_id: int,
            branch_id: int,
            scan_findings: List[FindingCreate],):
        for finding in scan_findings:
            logger.debug(self.format_commit_message(finding))

        logger.info(f"Found {len(scan_findings)} issues during scan: {scan_id} ")

    def write_scan(
            self,
            scan_type_to_run: ScanType,
            last_scanned_commit: str,
            scan_timestamp: datetime,
            branch: Branch,
            rule_pack: str) -> Optional[ScanRead]:
        logger.info(f"Running {scan_type_to_run} scan on branch {branch.branch_name}")
        return ScanRead(last_scanned_commit="NONE",
                        timestamp=datetime.now(),
                        branch_id=1,
                        id_=1,
                        rule_pack=rule_pack)

    def get_last_scanned_commit(self, branch: Branch):
        return None
