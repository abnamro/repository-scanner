# Standard Library
from datetime import datetime
from unittest.mock import call, patch

# Third Party
from resc_backend.resc_web_service.schema.branch import BranchBase, BranchRead
from resc_backend.resc_web_service.schema.finding import Finding
from resc_backend.resc_web_service.schema.finding_status import FindingStatus
from resc_backend.resc_web_service.schema.repository import RepositoryCreate, RepositoryRead
from resc_backend.resc_web_service.schema.scan import ScanRead

# First Party
from vcs_scanner.secret_scanners.stdout_writer import STDOUTWriter


# A test method to check the happy flow of the write_repository method.
@patch("logging.Logger.info")
def test_write_correct_repository(info_log):
    repository = RepositoryCreate(project_key="project_key",
                                  repository_id=1,
                                  repository_name="repository_name",
                                  repository_url="http://repository.url",
                                  vcs_instance=1)
    expected_call = f"Scanning repository {repository.project_key}/{repository.repository_name}"

    result = STDOUTWriter(toml_rule_file_path="toml_path", exit_code_warn=2, exit_code_block=1) \
        .write_repository(repository)
    assert result == repository
    info_log.assert_called_once_with(expected_call)


# A test method to check the happy flow of the write_branch method.
@patch("logging.Logger.info")
def test_write_correct_branch(info_log):
    repository = RepositoryRead(
        id_=1,
        project_key="project_key",
        repository_id="repository_id",
        repository_name="repository_name",
        repository_url="https://repo.url",
        vcs_instance=1
    )

    branch = BranchBase(branch_id=1,
                        branch_name="branch_name",
                        latest_commit="latest_commit")

    expected_call = f"Scanning branch {branch.branch_name} of repository {repository.repository_name}"

    result = STDOUTWriter(toml_rule_file_path="toml_path", exit_code_warn=2, exit_code_block=1) \
        .write_branch(repository, branch)
    assert result == branch
    info_log.assert_called_once_with(expected_call)


@patch("vcs_scanner.secret_scanners.stdout_writer.STDOUTWriter._get_rule_tags")
@patch("sys.exit")
@patch("logging.Logger.info")
def test_write_findings(info_log, exit_mock, _get_rule_tags):
    _get_rule_tags.return_value = {}
    findings = []
    for i in range(1, 6):
        findings.append(Finding(file_path=f"file_path_{i}",
                                line_number=i,
                                column_start=i,
                                column_end=i,
                                commit_id=f"commit_id_{i}",
                                commit_message=f"commit_message_{i}",
                                commit_timestamp=datetime.utcnow(),
                                author=f"author_{i}",
                                email=f"email_{i}",
                                status=FindingStatus.NOT_ANALYZED,
                                comment=f"comment_{i}",
                                event_sent_on=datetime.utcnow(),
                                rule_name=f"rule_{i}"))

    _ = STDOUTWriter(toml_rule_file_path="toml_path", exit_code_warn=2, exit_code_block=1) \
        .write_findings(1, 1, findings)
    calls = [call("Rule file: toml_path"),
             call('\n'
                  '+-------+--------+------+----------+-------------+\n'
                  '| Level | Rule   | Line | Position | File path   |\n'
                  '+-------+--------+------+----------+-------------+\n'
                  '| Info  | rule_1 |    1 | 1-1      | file_path_1 |\n'
                  '| Info  | rule_2 |    2 | 2-2      | file_path_2 |\n'
                  '| Info  | rule_3 |    3 | 3-3      | file_path_3 |\n'
                  '| Info  | rule_4 |    4 | 4-4      | file_path_4 |\n'
                  '| Info  | rule_5 |    5 | 5-5      | file_path_5 |\n'
                  '+-------+--------+------+----------+-------------+'),
             call("Findings detected : Total - 5, Block - 0, Warn - 0, Info - 5"),
             call("Findings threshold check results: PASS")]
    info_log.assert_has_calls(calls, any_order=True)
    exit_mock.assert_called_with(0)


@patch("logging.Logger.info")
def test_write_scan(info_log):
    rule_pack = "0.0.0"
    branch = BranchRead(id_=2,
                        branch_id="branch.branch_id",
                        branch_name="branch.branch_name",
                        latest_commit="latest_commit",
                        repository_id=1)
    expected_result = ScanRead(last_scanned_commit="NONE",
                               timestamp=datetime.now(),
                               branch_id=1,
                               id_=1,
                               rule_pack=rule_pack)
    expected_call = f"Running {expected_result.scan_type} scan on branch {branch.branch_name}"
    result = STDOUTWriter(toml_rule_file_path="toml_path", exit_code_warn=2, exit_code_block=1) \
        .write_scan(expected_result.scan_type, expected_result.last_scanned_commit, expected_result.timestamp, branch,
                    rule_pack=rule_pack)
    assert result.id_ == expected_result.id_
    assert result.branch_id == expected_result.branch_id
    assert result.rule_pack == expected_result.rule_pack
    assert result.last_scanned_commit == expected_result.last_scanned_commit
    info_log.assert_called_once_with(expected_call)


def test_get_last_scanned_commit():
    branch = BranchRead(id_=1,
                        branch_id="branch.branch_id",
                        branch_name="branch.branch_name",
                        latest_commit="latest_commit",
                        repository_id=1)

    result = STDOUTWriter(toml_rule_file_path="toml_path", exit_code_warn=2, exit_code_block=1) \
        .get_last_scanned_commit(branch)
    assert result is None
