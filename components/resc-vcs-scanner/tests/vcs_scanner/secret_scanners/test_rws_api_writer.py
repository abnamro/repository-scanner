# Standard Library
import json
import os
from datetime import datetime
from unittest.mock import patch

# Third Party
import pytest
from resc_backend.resc_web_service.schema.finding import Finding
from resc_backend.resc_web_service.schema.finding_status import FindingStatus
from resc_backend.resc_web_service.schema.repository import RepositoryCreate, RepositoryRead
from resc_backend.resc_web_service.schema.scan import ScanRead
from resc_backend.resc_web_service.schema.scan_type import ScanType

# First Party
from vcs_scanner.secret_scanners.rws_api_writer import RESTAPIWriter


# A test method to check the happy flow of the write_repository method.
@patch("requests.post")
def test_write_correct_repository(post):
    url = "https://nonexistingwebsite.com"

    repository = RepositoryCreate(project_key="project_key",
                                  repository_id=1,
                                  repository_name="repository_name",
                                  repository_url="http://repository.url",
                                  vcs_instance=1)
    expected_result = RepositoryRead(id_=1,
                                     project_key=repository.project_key,
                                     repository_id=repository.repository_id,
                                     repository_name=repository.repository_name,
                                     repository_url=repository.repository_url,
                                     vcs_instance=repository.vcs_instance)

    expected_json = expected_result.json()

    post.return_value.status_code = 201
    post.return_value.text = expected_json

    result = RESTAPIWriter(rws_url=url).write_repository(repository)
    assert result == expected_result


# A test method to check the result with incorrect repository information from the write_repository method.
@patch("requests.post")
@patch("logging.Logger.warning")
def test_write_incorrect_repository(warning, post):
    url = "https://nonexistingwebsite.com"

    repository = RepositoryCreate(project_key="project_key",
                                  repository_id=1,
                                  repository_name="repository_name",
                                  repository_url="http://repository.url",
                                  vcs_instance=1)
    expected_result = RepositoryRead(id_=1,
                                     project_key=repository.project_key,
                                     repository_id=repository.repository_id,
                                     repository_name=repository.repository_name,
                                     repository_url=repository.repository_url,
                                     vcs_instance=repository.vcs_instance)

    expected_json = expected_result.json()

    post.return_value.status_code = 404
    post.return_value.text = expected_json

    result = RESTAPIWriter(rws_url=url).write_repository(repository)
    assert result is None
    warning.assert_called_once()
    warning.assert_called_with(f"Creating repository failed with error: {404}->{expected_json}")


@patch("requests.post")
@patch("logging.Logger.info")
def test_write_findings(info, post):
    url = "https://nonexistingwebsite.com"
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

    post.return_value.status_code = 201
    post.return_value.text = len(findings)

    _ = RESTAPIWriter(rws_url=url).write_findings(1, 1, findings)
    info.assert_called_once()
    info.assert_called_with(f"Found {len(findings)} issues during scan for scan_id: {1} ")


@patch("requests.post")
@patch("logging.Logger.warning")
def test_write_findings_unsuccessful(warning, post):
    url = "https://nonexistingwebsite.com"
    findings = []

    post.return_value.status_code = 400
    post.return_value.text = len(findings)

    _ = RESTAPIWriter(rws_url=url).write_findings(1, 1, findings)
    warning.assert_called_once()
    warning.assert_called_with(f"Creating findings for scan {1} "
                               f"failed with error: {400}->{0}")


@patch("requests.post")
def test_write_scan(post):
    url = "https://nonexistingwebsite.com"
    repository = RepositoryRead(id_=1,
                                project_key="project_key",
                                repository_id=1,
                                repository_name="repository_name",
                                repository_url="http://repository.url",
                                vcs_instance=1)
    expected_result = ScanRead(id_=1,
                               scan_type=ScanType.BASE,
                               last_scanned_commit="123456789abcdef",
                               timestamp=datetime.now(),
                               increment_number=0,
                               repository_id=repository.id_,
                               rule_pack="0.0.0")

    expected_json = expected_result.json()

    post.return_value.status_code = 201
    post.return_value.text = expected_json

    result = RESTAPIWriter(rws_url=url).write_scan(expected_result.scan_type, expected_result.last_scanned_commit,
                                                   expected_result.timestamp, repository, rule_pack="0.0.0")
    assert result == expected_result


@patch("requests.post")
@patch("logging.Logger.warning")
def test_write_scan_unsuccessful(warning, post):
    url = "https://nonexistingwebsite.com"
    repository = RepositoryRead(id_=1,
                                project_key="project_key",
                                repository_id=1,
                                repository_name="repository_name",
                                repository_url="http://repository.url",
                                vcs_instance=1)
    expected_result = ScanRead(id_=1,
                               scan_type=ScanType.BASE,
                               last_scanned_commit="123456789abcdef",
                               timestamp=datetime.now(),
                               increment_number=0,
                               repository_id=repository.id_,
                               rule_pack="0.0.0")

    expected_json = expected_result.json()

    post.return_value.status_code = 400
    post.return_value.text = expected_json

    result = RESTAPIWriter(rws_url=url).write_scan(expected_result.scan_type, expected_result.last_scanned_commit,
                                                   expected_result.timestamp, repository, rule_pack="0.0.0")
    assert result is None
    warning.assert_called_once()
    warning.assert_called_with(
        f"Creating {expected_result.scan_type} scan failed with error: {400}->{expected_json}")


@patch("requests.get")
def test_get_last_scan_for_repository(get):
    url = "https://nonexistingwebsite.com"
    repository = RepositoryRead(id_=1,
                                project_key="project_key",
                                repository_id=1,
                                repository_name="repository_name",
                                repository_url="http://repository.url",
                                vcs_instance=1)
    expected_result = ScanRead(id_=1,
                               last_scanned_commit="561dsf651t34544",
                               timestamp=datetime.now(),
                               increment_number=0,
                               repository_id=1,
                               rule_pack="0.0.0")

    expected_json = expected_result.json()

    get.return_value.status_code = 200
    get.return_value.text = expected_json

    result = RESTAPIWriter(rws_url=url).get_last_scan_for_repository(repository)
    assert result == expected_result


@patch("requests.get")
@patch("logging.Logger.warning")
def test_get_last_scanned_commit_invalid_id(warning, get):
    repository = RepositoryRead(id_=2,
                                project_key="project_key",
                                repository_id=1,
                                repository_name="repository_name",
                                repository_url="http://repository.url",
                                vcs_instance=1)
    url = "https://nonexistingwebsite.com"
    error_text = "Unable to retrieve scan for id"
    get.return_value.status_code = 404
    get.return_value.text = error_text

    result = RESTAPIWriter(rws_url=url).get_last_scan_for_repository(repository)
    assert result is None
    warning.assert_called_once()
    warning.assert_called_with(f"Retrieving last scan details failed with error: 404->{error_text}")


@patch("requests.get")
@patch("logging.Logger.debug")
def test_download_rule_pack_successful(debug, get):
    url = "https://nonexistingwebsite.com"
    get.return_value.status_code = 200
    get.return_value.content = "test-data".encode()
    rule_pack_version = "0.0.1"
    out_file_path = "/tmp/temp_resc_rule.toml"

    result = RESTAPIWriter(rws_url=url).download_rule_pack(rule_pack_version)
    file_exists = os.path.exists(out_file_path)
    file_contents = open(out_file_path).read()

    assert result is rule_pack_version
    assert file_exists is True
    assert file_contents == "test-data"
    debug.assert_called_with(
        f"Rule pack version: {rule_pack_version} has been successfully downloaded to location {out_file_path}")

    os.remove(out_file_path)


@patch("requests.get")
@patch("logging.Logger.error")
def test_download_rule_pack_unsuccessful(error, get):
    url = "https://nonexistingwebsite.com"
    error_text = "Unable to retrieve rule pack"
    get.return_value.status_code = 404
    get.return_value.text = error_text
    rule_pack_version = "0.0.1"

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        result = RESTAPIWriter(rws_url=url).download_rule_pack(rule_pack_version)
        assert result is None
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == -1
        error.assert_called_once()
        error.assert_called_with(f"Aborting scan! Downloading rule pack version {rule_pack_version} failed with "
                                 f"error: {get.return_value.status_code}->{get.return_value.text}")


@patch("vcs_scanner.secret_scanners.rws_api_writer.RESTAPIWriter.get_active_rule_pack_version")
@patch("vcs_scanner.secret_scanners.rws_api_writer.RESTAPIWriter.download_rule_pack")
def test_check_active_rule_pack_version_when_version_provided_equals_to_active_rule_pack_version(
        download_rule_pack,
        get_active_rule_pack_version):
    url = "https://nonexistingwebsite.com"
    version = "0.0.1"
    get_active_rule_pack_version.return_value = "0.0.1"
    download_rule_pack.return_value = "0.0.1"

    rule_pack_version = RESTAPIWriter(rws_url=url).check_active_rule_pack_version(rule_pack_version=version)
    assert rule_pack_version is get_active_rule_pack_version.return_value


@patch("vcs_scanner.secret_scanners.rws_api_writer.RESTAPIWriter.get_active_rule_pack_version")
@patch("vcs_scanner.secret_scanners.rws_api_writer.RESTAPIWriter.download_rule_pack")
def test_check_active_rule_pack_version_when_version_provided_not_equals_to_active_rule_pack_version(
        download_rule_pack,
        get_active_rule_pack_version):
    url = "https://nonexistingwebsite.com"
    rule_pack_version = "0.0.1"
    get_active_rule_pack_version.return_value = "0.0.2"
    download_rule_pack.return_value = "0.0.2"

    rule_pack_version = RESTAPIWriter(rws_url=url).check_active_rule_pack_version(rule_pack_version=rule_pack_version)
    assert rule_pack_version is download_rule_pack.return_value


@patch("vcs_scanner.secret_scanners.rws_api_writer.RESTAPIWriter.download_rule_pack")
def test_check_active_rule_pack_version_when_rule_pack_version_not_provided(download_rule_pack):
    url = "https://nonexistingwebsite.com"
    rule_pack_version = None
    download_rule_pack.return_value = "0.0.1"

    rule_pack_version = RESTAPIWriter(rws_url=url).check_active_rule_pack_version(rule_pack_version=rule_pack_version)
    assert rule_pack_version is download_rule_pack.return_value


@patch("requests.get")
def test_get_active_rule_pack_version_successful(get):
    url = "https://nonexistingwebsite.com"
    expected_result = '{"data": [ {"version": "1.0.0", "active": "true", "global_allow_list": 1}], "total": 1, ' \
                      '"limit": 100, "skip": 0} '
    get.return_value.status_code = 200
    get.return_value.text = expected_result

    result = RESTAPIWriter(rws_url=url).get_active_rule_pack_version()
    assert result == json.loads(expected_result)["data"][0]["version"]


@patch("requests.get")
@patch("logging.Logger.warning")
def test_get_active_rule_pack_version_unsuccessful(warning, get):
    url = "https://nonexistingwebsite.com"
    error_text = "Unable to retrieve active rule pack"
    get.return_value.status_code = 404
    get.return_value.text = error_text

    result = RESTAPIWriter(rws_url=url).get_active_rule_pack_version()
    assert result is None
    warning.assert_called_once()
    warning.assert_called_with(
        f"Retrieving active rule pack version failed with error: {get.return_value.status_code}->{error_text}")
