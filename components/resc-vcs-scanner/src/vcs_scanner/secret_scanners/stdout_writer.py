# Standard Library
import logging
from datetime import datetime
from typing import List, Optional

# Third Party
import tomlkit
from prettytable import PrettyTable
from resc_backend.resc_web_service.schema.branch import Branch
from resc_backend.resc_web_service.schema.finding import FindingCreate
from resc_backend.resc_web_service.schema.repository import Repository
from resc_backend.resc_web_service.schema.scan import ScanRead
from resc_backend.resc_web_service.schema.scan_type import ScanType
from resc_backend.resc_web_service.schema.vcs_instance import VCSInstanceRead

# First Party
from vcs_scanner.helpers.finding_action import FindingAction
from vcs_scanner.model import VCSInstanceRuntime
from vcs_scanner.output_module import OutputModule

logger = logging.getLogger(__name__)


class STDOUTWriter(OutputModule):

    def __init__(self, toml_rule_file_path: str):
        self.toml_rule_file_path: str = toml_rule_file_path

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

    def _get_rule_tags(self) -> dict:
        rule_tags = {}
        # read toml
        with open(self.toml_rule_file_path, encoding="utf-8") as toml_rule_file:
            toml_rule_dictionary = tomlkit.loads(toml_rule_file.read())
            # convert to dict
            for toml_rule in toml_rule_dictionary["rules"]:
                rule_id = toml_rule.get('id', None)
                if rule_id:
                    rule_tags[rule_id] = toml_rule.get('tags', [])
        return rule_tags

    @staticmethod
    def _determine_finding_action(finding: FindingCreate, rule_tags: dict) -> FindingAction:
        rule_action = FindingAction.INFO
        if FindingAction.WARN in rule_tags[finding.rule_name]:
            rule_action = FindingAction.WARN
        if FindingAction.BLOCK in rule_tags[finding.rule_name]:
            rule_action = FindingAction.BLOCK
        return rule_action

    def write_findings(self, scan_id: int, branch_id: int, scan_findings: List[FindingCreate]):
        # Initialize table
        output_table = PrettyTable()
        output_table.field_names = ['Level', 'Rule', 'Line', 'File path']
        output_table.align = 'l'
        output_table.align['Line'] = 'r'

        scan_has_warnings = False
        scan_has_blockers = False

        rule_tags = self._get_rule_tags()
        for finding in scan_findings:
            finding_action = self._determine_finding_action(finding, rule_tags)

            scan_has_warnings = True if finding_action == FindingAction.WARN else scan_has_warnings
            scan_has_blockers = True if finding_action == FindingAction.BLOCK else scan_has_blockers

            output_table.add_row([finding_action.value, finding.rule_name, finding.line_number, finding.file_path])

        logger.info(f"\n{output_table.get_string(sortby='Rule')}")
        logger.info(f"Found {len(scan_findings)} findings {self.toml_rule_file_path}"
                    f" has_warnings {scan_has_warnings} has_blockers {scan_has_blockers}")

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
