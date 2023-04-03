# Standard Library
import logging
import sys
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
from termcolor import colored

# First Party
from vcs_scanner.helpers.finding_action import FindingAction
from vcs_scanner.model import VCSInstanceRuntime
from vcs_scanner.output_module import OutputModule

logger = logging.getLogger(__name__)


class STDOUTWriter(OutputModule):

    def __init__(self, toml_rule_file_path: str, exit_code_warn: int, exit_code_block: int, filter_tag: str = None):
        self.toml_rule_file_path: str = toml_rule_file_path
        self.exit_code_warn: int = exit_code_warn
        self.exit_code_block: int = exit_code_block
        self.filter_tag: str = filter_tag
        self.exit_code_success = 0

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
        """
            Get the tags per rule from the .toml rule file, from self.toml_rule_file_path
        :return: dict.
            The output will contain a dictionary with the rule id as the key and the tags as a list in the value
        """
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
        """
            Determine the action to take for the finding, based on the rule tags
        :param finding:
            FindingCreate instance of the finding
        :param rule_tags:
            Dictionary continuing all the rules and there respective tags
        :return: FindingAction.
            FindingAction to take for this finding
        """
        rule_action = FindingAction.INFO
        if FindingAction.WARN in rule_tags.get(finding.rule_name, []):
            rule_action = FindingAction.WARN
        if FindingAction.BLOCK in rule_tags.get(finding.rule_name, []):
            rule_action = FindingAction.BLOCK
        return rule_action

    def _finding_tag_filter(self, finding: FindingCreate, rule_tags: dict, filter_tag: str) -> bool:
        """
            Determine the action to take for the finding, based on the rule tags
        :param finding:
            FindingCreate instance of the finding
        :param rule_tags:
            Dictionary continuing all the rules and there respective tags
        :Param: filter_tag.
            filter_tag will check for the tag
        :return bool:
            The output will be boolean, based on the tag filter given
        """
        if filter_tag and filter_tag not in rule_tags.get(finding.rule_name, []):
            return False
        return True

    def write_findings(self, scan_id: int, branch_id: int, scan_findings: List[FindingCreate]):
        """
            Write the findings to the STDOUT in a nice table and set the exit code based on the FindingActions found
        :param scan_id:
            id of the scan in question
        :param branch_id:
            id of the branch in question
        :param scan_findings:
            List of FindingCreate of all the findings from the scan
        """
        # Initialize table
        output_table = PrettyTable()
        output_table.field_names = ['Level', 'Rule', 'Line', 'Position', 'File path']
        output_table.align = 'l'
        output_table.align['Line'] = 'r'

        block_count = 0
        warn_count = 0
        info_count = 0

        exit_code = self.exit_code_success

        rule_tags = self._get_rule_tags()
        for finding in scan_findings:
            should_process_finding = self._finding_tag_filter(finding, rule_tags, self.filter_tag)
            if should_process_finding:
                finding_action = self._determine_finding_action(finding, rule_tags)
                if finding_action == FindingAction.BLOCK:
                    finding_action_value = colored(finding_action.value, "red", attrs=["bold"])
                    block_count += 1
                elif finding_action == FindingAction.WARN:
                    finding_action_value = colored(finding_action.value, "light_red", attrs=["bold"])
                    warn_count += 1
                elif finding_action == FindingAction.INFO:
                    finding_action_value = colored(finding_action.value, "light_yellow", attrs=["bold"])
                    info_count += 1
                else:
                    finding_action_value = finding_action.value
                    info_count += 1

                if exit_code != self.exit_code_block:
                    if exit_code == self.exit_code_success and finding_action == FindingAction.WARN:
                        exit_code = self.exit_code_warn
                    elif finding_action == FindingAction.BLOCK:
                        exit_code = self.exit_code_block

                output_table.add_row([finding_action_value, finding.rule_name, finding.line_number,
                                     f"{finding.column_start}-{finding.column_end}", finding.file_path])

        logger.info(f"\n{output_table.get_string(sortby='Level')}")

        logger.info(f"Findings detected : Total - {block_count+warn_count+info_count}, Block - {block_count}, "
                    f"Warn - {warn_count}, Info - {info_count}")

        if exit_code == self.exit_code_success:
            logger.info(f"Findings threshold check results: {colored('PASS', 'light_green', attrs=['bold'])}")
        elif exit_code == self.exit_code_block:
            logger.info(f"Findings threshold check results: {colored('FAIL', 'red', attrs=['bold'])}")
            logger.info(
                colored(f"Scan failed due to policy violations: [Block:{block_count}]", "red", attrs=["bold"]))
        elif exit_code == self.exit_code_warn:
            logger.info(f"Findings threshold check results: {colored('PASS', 'light_green', attrs=['bold'])}")
            logger.info(colored(f"Warning for policy violations: [Warn:{warn_count}]", "light_red", attrs=["bold"]))

        sys.exit(exit_code)

    def write_scan(self, scan_type_to_run: ScanType, last_scanned_commit: str, scan_timestamp: datetime,
                   branch: Branch, rule_pack: str) -> Optional[ScanRead]:
        logger.info(f"Running {scan_type_to_run} scan on branch {branch.branch_name}")
        return ScanRead(last_scanned_commit="NONE",
                        timestamp=datetime.now(),
                        branch_id=1,
                        id_=1,
                        rule_pack=rule_pack)

    def get_last_scanned_commit(self, branch: Branch):
        return None
