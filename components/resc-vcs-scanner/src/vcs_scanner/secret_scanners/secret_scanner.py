# pylint: disable=E1101
# Standard Library
import logging
import os
import shutil
import time
import uuid
from datetime import datetime
from typing import List, Optional

# Third Party
from resc_backend.resc_web_service.schema.finding import FindingBase
from resc_backend.resc_web_service.schema.repository import Repository
from resc_backend.resc_web_service.schema.scan import Scan
from resc_backend.resc_web_service.schema.scan_type import ScanType

# First Party
from vcs_scanner.output_module import OutputModule
from vcs_scanner.resc_worker import RESCWorker
from vcs_scanner.secret_scanners.git_operation import clone_repository
from vcs_scanner.secret_scanners.gitleaks_wrapper import GitLeaksWrapper

# This is an arbitrary number to distinguish between no issues, an error and
# the situation in which leaks are found. Note that this number cannot be bigger than 255 (OS limitation)
LEAKS_FOUND_EXIT_CODE = 42
NO_LEAKS_FOUND_EXIT_CODE = 0

logger = logging.getLogger(__name__)


class SecretScanner(RESCWorker):  # pylint: disable=R0902

    def __init__(self,
                 gitleaks_binary_path: str,
                 gitleaks_rules_path: str,
                 rule_pack_version: str,
                 output_plugin: OutputModule,
                 repository: Repository,
                 username: str,
                 personal_access_token: str,
                 scan_tmp_directory: str = ".",
                 local_path: str = None,
                 force_base_scan: bool = False,
                 latest_commit: str = None):

        self.gitleaks_rules_path: str = gitleaks_rules_path
        self.gitleaks_binary_path: str = gitleaks_binary_path
        self.rule_pack_version: str = rule_pack_version
        self._output_module: OutputModule = output_plugin
        self._scan_tmp_directory: str = scan_tmp_directory
        self.repository: Repository = repository
        self.username: str = username
        self.personal_access_token: str = personal_access_token
        self.local_path = local_path
        self.force_base_scan = force_base_scan
        self.latest_commit = latest_commit
        if self.local_path:
            self.repo_display_name = self.local_path.replace(".", "_").replace("/", "_")
        else:
            self.repo_display_name = self.repository.repository_url

    def clone_repo(self) -> str:
        repo_clone_path = f"{self._scan_tmp_directory}/{self.repository.repository_name}"
        clone_repository(self.repository.repository_url, repo_clone_path, username=self.username,
                         personal_access_token=self.personal_access_token)
        return repo_clone_path

    def run_repository_scan(self) -> None:
        logger.info(
            f"Started task for scanning {self.repository.repository_name} using "
            f"rule pack version: {self.rule_pack_version}")

        # Insert in to repository table
        created_repository = self._output_module.write_repository(self.repository)
        if not created_repository:
            logger.error(f"Error processing "
                         f"{self.repository.repository_name}."
                         f" Error details: unable to create repository: {created_repository}")
            return

        logger.info(f"Scanning repository {self.repository.project_key}/{self.repository.repository_name}")

        # Get last scanned commit for the repository
        last_scan_for_repository = self._output_module.get_last_scan_for_repository(repository=created_repository)
        last_scanned_commit = last_scan_for_repository.last_scanned_commit if last_scan_for_repository else None
        scan_type_to_run = self.determine_scan_type(latest_commit=self.latest_commit,
                                                    last_scan_for_repository=last_scan_for_repository)

        if scan_type_to_run:
            # Insert in to scan table
            scan_timestamp_start = datetime.utcnow()
            created_scan = self._output_module.write_scan(
                scan_type_to_run, self.latest_commit,
                scan_timestamp_start.isoformat(), created_repository,
                rule_pack=self.rule_pack_version)
            if not created_scan:
                logger.error(f"Error processing {self.repository.project_key}/{self.repository.repository_name} "
                             f"Error details: unable to create scan object")
                return

            # Clone and run scan upon the repository
            if not self.local_path:
                repo_clone_path: str = self.clone_repo()
            else:
                repo_clone_path = self.local_path

            findings = self.scan_repo(scan_type_to_run, last_scanned_commit, repo_clone_path)
            scan_timestamp_end = datetime.utcnow()
            logger.info(f"Running {scan_type_to_run} scan on repository "
                        f"{self.repository.project_key}/{self.repository.repository_name}"
                        f" took {scan_timestamp_end - scan_timestamp_start} ms.")

            if findings:
                logger.info(f"Scan completed: {len(findings)} findings were found.")
                self._output_module.write_findings(repository_id=created_repository.id_, scan_id=created_scan.id_,
                                                   scan_findings=findings)
            else:
                logger.info("No findings registered in "
                            f"{self.repository.project_key}/{self.repository.repository_name}")
        else:
            logger.info(f"Skipped {scan_type_to_run} scanning on repository: "
                        f"{self.repository.project_key}/{self.repository.repository_name} no new commits found.")

    def run_directory_scan(self) -> None:
        """
            Scan the given non-git directory, set in the self.local_path variable
        """
        logger.info(f"Started task for scanning {self.local_path} using rule pack version: {self.rule_pack_version}")

        scan_timestamp_start = datetime.utcnow()
        findings = self.scan_directory(self.local_path)
        scan_timestamp_end = datetime.utcnow()
        logger.info(f"Running local scan on {self.local_path} took {scan_timestamp_end - scan_timestamp_start} ms.")

        if findings:
            logger.info(f"Scan completed: {len(findings)} findings were found.")
            self._output_module.write_findings(repository_id=0, scan_id=0, scan_findings=findings)
        else:
            logger.info(f"No findings registered in {self.local_path}.")

    def scan_repo(self, scan_type_to_run: str, last_scanned_commit: str, repo_clone_path: str) \
            -> Optional[List[FindingBase]]:

        """
            Clone and scan the given repository
        :param repo_clone_path:
            Directory path where the repository has already been cloned
        :param scan_type_to_run:
            Type of scan to run (Base or Incremental)
        :param last_scanned_commit:
            Last scanned commit of the repository to scan
        :return: Success, output.
            If Success is False, the output will contain an error message.
            Otherwise, the output will contain a list of findings or an empty list if no issue was found
        """

        logger.debug(f"Started scanning {self.repo_display_name}")
        if not self.local_path:
            report_filepath = f"{self._scan_tmp_directory}/{repo_clone_path}_{str(uuid.uuid4().hex)}.json"
        else:
            report_filepath = f"{self.local_path}/{self.repo_display_name}_{str(uuid.uuid4().hex)}.json"
        try:

            if scan_type_to_run == ScanType.BASE:
                scan_from = None
            elif scan_type_to_run == ScanType.INCREMENTAL and last_scanned_commit:
                scan_from = last_scanned_commit
            else:
                scan_from = None

            gitleaks_command = GitLeaksWrapper(
                scan_from=scan_from,
                gitleaks_path=self.gitleaks_binary_path,
                repository_path=repo_clone_path,
                rules_filepath=self.gitleaks_rules_path,
                report_filepath=report_filepath)

            before_scan = time.time()
            findings: Optional[List[FindingBase]] = gitleaks_command.start_scan()
            after_scan = time.time()
            scan_duration = int(after_scan - before_scan)
            logger.info(f"scan of repository {repo_clone_path} took {scan_duration} seconds")
            return findings
        except BaseException as error:
            logger.error(f"An exception occurred while scanning repository {self.repository.repository_url} "
                         f"error: {error}")
        finally:
            # Make sure the tempfile and repo cloned path removed
            logger.debug(f"Cleaning up the temporary report: {report_filepath}")
            if os.path.exists(report_filepath):
                os.remove(report_filepath)
            if repo_clone_path and not self.local_path and os.path.exists(repo_clone_path):
                logger.debug(f"Cleaning up the repository cloned directory: {repo_clone_path}")
                shutil.rmtree(repo_clone_path)
        return None

    def scan_directory(self, directory_path: str) -> Optional[List[FindingBase]]:
        """
            Scan the given directory
        :param directory_path:
            Directory path to be scanned
        :return: Optional[List[FindingBase]].
            The output will contain a list of findings or an empty list if no finding was found
        """
        logger.debug(f"Started scanning {self.repo_display_name}:{directory_path}")
        if not self.local_path:
            report_filepath = f"{self._scan_tmp_directory}/{directory_path}_{str(uuid.uuid4().hex)}.json"
        else:
            report_filepath = f"{self.local_path}/{self.repo_display_name}_{str(uuid.uuid4().hex)}.json"
        try:
            gitleaks_command = GitLeaksWrapper(
                scan_from=None,
                gitleaks_path=self.gitleaks_binary_path,
                repository_path=directory_path,
                rules_filepath=self.gitleaks_rules_path,
                report_filepath=report_filepath,
                git_scan=False
            )

            before_scan = time.time()
            findings: Optional[List[FindingBase]] = gitleaks_command.start_scan()
            after_scan = time.time()
            scan_duration = int(after_scan - before_scan)
            logger.info(f"scan of repository {directory_path} took {scan_duration} seconds")
            return findings
        except BaseException as error:
            logger.error(f"An exception occurred while scanning directory {directory_path} error: {error}")
        finally:
            # Make sure the tempfile is removed
            logger.debug(f"Cleaning up the temporary report: {report_filepath}")
            if os.path.exists(report_filepath):
                os.remove(report_filepath)
        return None

    # Decide which type of scan to run
    def determine_scan_type(self, last_scan_for_repository: Scan, latest_commit: str = None):
        # Force base scan, or has no previous scan
        if self.force_base_scan or last_scan_for_repository is None:
            return ScanType.BASE
        # Has previous scan
        if last_scan_for_repository:
            # Rule-pack is different from previous scan
            if last_scan_for_repository.rule_pack != self.rule_pack_version:
                return ScanType.BASE
            # Last commit is different from previous scan
            if latest_commit and latest_commit != last_scan_for_repository.last_scanned_commit:
                return ScanType.INCREMENTAL
        # Skip scanning, no conditions match
        return None
