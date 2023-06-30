# Standard Library
from datetime import datetime
from unittest.mock import call, patch

# Third Party
from resc_backend.resc_web_service.schema.finding import Finding, FindingCreate
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
    calls = [call('\n'
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
    repository = RepositoryRead(id_=1,
                                project_key="project_key",
                                repository_id=1,
                                repository_name="repository_name",
                                repository_url="http://repository.url",
                                vcs_instance=1)
    expected_result = ScanRead(last_scanned_commit="NONE",
                               timestamp=datetime.now(),
                               repository_id=1,
                               id_=1,
                               rule_pack=rule_pack)
    expected_call = f"Running {expected_result.scan_type} scan on repository {repository.repository_url}"
    result = STDOUTWriter(toml_rule_file_path="toml_path", exit_code_warn=2, exit_code_block=1) \
        .write_scan(expected_result.scan_type, expected_result.last_scanned_commit, expected_result.timestamp,
                    repository, rule_pack=rule_pack)
    assert result.id_ == expected_result.id_
    assert result.repository_id == expected_result.repository_id
    assert result.rule_pack == expected_result.rule_pack
    assert result.last_scanned_commit == expected_result.last_scanned_commit
    info_log.assert_called_once_with(expected_call)


def test_get_last_scanned_commit():
    repository = RepositoryRead(id_=1,
                                project_key="project_key",
                                repository_id=1,
                                repository_name="repository_name",
                                repository_url="http://repository.url",
                                vcs_instance=1)

    result = STDOUTWriter(toml_rule_file_path="toml_path", exit_code_warn=2, exit_code_block=1) \
        .get_last_scan_for_repository(repository)
    assert result is None


def test_finding_tag_filter_no_filter():
    finding = FindingCreate(scan_ids=[1],
                            file_path=f"file_path_{1}",
                            line_number=1,
                            column_start=1,
                            column_end=1,
                            commit_id=f"commit_id_{1}",
                            commit_message=f"commit_message_{1}",
                            commit_timestamp=datetime.utcnow(),
                            author=f"author_{1}",
                            email=f"email_{1}",
                            status=FindingStatus.NOT_ANALYZED,
                            comment=f"comment_{1}",
                            rule_name=f"rule_{1}",
                            repository_id=1)

    result = STDOUTWriter(toml_rule_file_path="toml_path", exit_code_warn=2, exit_code_block=1) \
        ._finding_tag_filter(finding=finding, rule_tags={"rule_1": ["tag"]}, filter_tag=None)
    assert result is True


def test_finding_tag_filter_match_filter():
    finding = FindingCreate(scan_ids=[1],
                            file_path=f"file_path_{1}",
                            line_number=1,
                            column_start=1,
                            column_end=1,
                            commit_id=f"commit_id_{1}",
                            commit_message=f"commit_message_{1}",
                            commit_timestamp=datetime.utcnow(),
                            author=f"author_{1}",
                            email=f"email_{1}",
                            status=FindingStatus.NOT_ANALYZED,
                            comment=f"comment_{1}",
                            rule_name=f"rule_{1}",
                            repository_id=1)

    result = STDOUTWriter(toml_rule_file_path="toml_path", exit_code_warn=2, exit_code_block=1) \
        ._finding_tag_filter(finding=finding, rule_tags={"rule_1": ["tag"]}, filter_tag="tag")
    assert result is True


def test_finding_tag_filter_nomatch_filter():
    finding = FindingCreate(scan_ids=[1],
                            file_path=f"file_path_{1}",
                            line_number=1,
                            column_start=1,
                            column_end=1,
                            commit_id=f"commit_id_{1}",
                            commit_message=f"commit_message_{1}",
                            commit_timestamp=datetime.utcnow(),
                            author=f"author_{1}",
                            email=f"email_{1}",
                            status=FindingStatus.NOT_ANALYZED,
                            comment=f"comment_{1}",
                            rule_name=f"rule_{1}",
                            repository_id=1)

    result = STDOUTWriter(toml_rule_file_path="toml_path", exit_code_warn=2, exit_code_block=1) \
        ._finding_tag_filter(finding=finding, rule_tags={"rule_1": ["tag"]}, filter_tag="resc")
    assert result is False
