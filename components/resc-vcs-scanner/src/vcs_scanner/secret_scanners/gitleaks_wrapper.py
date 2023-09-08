# Standard Library
import datetime
import json
import logging
import subprocess
from typing import List, Optional

# Third Party
from resc_backend.resc_web_service.schema.finding import FindingBase

# First Party
from vcs_scanner.constants import LEAKS_FOUND_EXIT_CODE, NO_LEAKS_FOUND_EXIT_CODE

logger: logging.Logger = logging.getLogger(__name__)


class GitLeaksWrapper:
    SCAN_TMP_DIRECTORY: str = "."

    def __init__(self, rules_filepath: str,
                 report_filepath: str, repository_path: str,
                 scan_from: str = None, gitleaks_path: str = "gitleaks",
                 git_scan: bool = True):

        self.rules_filepath = rules_filepath
        self.report_filepath = report_filepath
        self.repository_path = repository_path
        self.scan_from = scan_from
        self.gitleaks_path = gitleaks_path
        self.git_scan = git_scan

    def _build_gitleaks_command(self):

        # Base scan command
        command = [f"{self.gitleaks_path}",
                   "detect",
                   f"--source={self.repository_path}",
                   f"--config={self.rules_filepath}",
                   f"--report-path={self.report_filepath}",
                   f"--exit-code={LEAKS_FOUND_EXIT_CODE}"]

        if not self.git_scan:
            command.append("--no-git")

        # Incremental scan command
        if self.scan_from:
            command.append(f"--log-opts={self.scan_from}..")
        return command

    def start_scan(self) -> Optional[List[FindingBase]]:
        """
        :return: Output.
            If Successful, a list of FindingCreate objects is returned.
            Otherwise, a None object is returned
        """
        try:
            result = subprocess.run(
                self._build_gitleaks_command(),
                check=False, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            exitcode = result.returncode
            if exitcode == NO_LEAKS_FOUND_EXIT_CODE:
                return []
            if exitcode == LEAKS_FOUND_EXIT_CODE:
                return self._parse_output(self.report_filepath)

            error_output = result.stderr.decode("utf-8")
            logger.error(f"GitLeaks exited with an unexpected code: {exitcode}. Output: {error_output}")
            return None

        except subprocess.CalledProcessError as called_process_error:
            logger.error(
                f"Error encountered while running the gitleaks process: {called_process_error.stdout.decode('utf-8')}")
            return None
        except FileNotFoundError as error:
            logger.error(f"Unable to locate a file: {error}")
            return None

    @staticmethod
    def _calculate_permanent_leak_url(leak_url: str, repository: str, commit_id: str) -> str:
        """
            The Leak URL given by bitbucket is not correct.
            Construct a proper one that links to the exact change in the commit
        :param leak_url: The url of the leak (Bitbucket format)
        :param repository: The git repository
        :param commit_id: The commit hash
        :return: the permalink to the leak
        """
        new_url = leak_url

        # Remove the line-number from the url.
        hash_pos = new_url.rfind("#")
        if hash_pos > 0:
            new_url = new_url[:hash_pos]

        new_url = new_url.replace("/scm/", "/projects/")
        new_url = new_url.replace("/blob/", "/commits/")
        new_url = new_url.replace(f"/{repository}/", f"/repos/{repository[:-4]}/")  # remove .git at the end
        new_url = new_url.replace(f"/{commit_id}/", f"/{commit_id}#")

        return new_url

    @staticmethod
    def _is_valid_timestamp(timestamp: str) -> Optional[datetime.datetime]:
        try:
            converted_timestamp: Optional[datetime.datetime] = \
                datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S%z")
        except ValueError:
            converted_timestamp = None
        return converted_timestamp

    @classmethod
    def _parse_output(cls, file_path: str) -> List[FindingBase]:
        """
        Parse the gitleaks findings from the temp file and return a list of Finding objects
        :param file_path: the tempfile containing the gitleaks findings
        :return: list of Finding objects
        """
        findings = []
        with open(file_path, encoding="utf-8") as report_file:
            results = json.load(report_file)

        for result in results:
            commit_timestamp = cls._is_valid_timestamp(result["Date"])
            if not commit_timestamp:
                logger.debug(f"{result['Date']} has an unexpected date format. Expected ISO 8601")
                commit_timestamp = datetime.datetime.now()
            finding = FindingBase(file_path=result["File"],
                                  line_number=result["StartLine"],
                                  column_start=result["StartColumn"],
                                  column_end=result["EndColumn"],
                                  email=result["Email"],
                                  author=result["Author"],
                                  commit_id=result["Commit"],
                                  commit_message=result["Message"],
                                  commit_timestamp=commit_timestamp,
                                  rule_name=result["RuleID"])

            findings.append(finding)

        return findings
