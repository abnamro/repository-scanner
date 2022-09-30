# Standard Library
import sys
from unittest.mock import patch

# Third Party
from _pytest.monkeypatch import MonkeyPatch
from repository_scanner_backend.resc_web_service.schema.branch_info import BranchInfo
from repository_scanner_backend.resc_web_service.schema.repository_info import RepositoryInfo
from repository_scanner_backend.resc_web_service.schema.scan_type import ScanType

# First Party
from repository_scanners.secret_scanners.rws_api_writer import RESTAPIWriter

sys.path.insert(0, "src")

mp = MonkeyPatch()
mp.setenv('GITLEAKS_PATH', 'fake_gitleaks_path')
mp.setenv('RESC_RABBITMQ_SERVICE_HOST', 'fake-rabbitmq-host.fakehost.com')
mp.setenv('RABBITMQ_DEFAULT_VHOST', 'vhost')
mp.setenv('RESC_API_NO_AUTH_SERVICE_HOST', 'fake_api_service_host')
mp.setenv('RABBITMQ_USERNAME', 'fake user')
mp.setenv('RABBITMQ_PASSWORD', 'fake pass')
mp.setenv('RABBITMQ_QUEUE', 'queuename')
mp.setenv('VCS_INSTANCES_FILE_PATH', 'fake_vcs_instance_config_json_path')

from repository_scanners.secret_scanners.secret_scanner import SecretScanner  # noqa: E402  # isort:skip

BITBUCKET_USERNAME = "test"
GITLEAKS_PATH = "gitleaks_exec"


@patch("git.repo.base.Repo.clone_from")
def test_clone_repo(clone_from):
    rws_url = "https://fakeurl.com:8000"
    username = "username"
    personal_access_token = "personal_access_token"

    branches = []
    for i in range(1, 6):
        branches.append(BranchInfo(branch_id=i,
                                   branch_name=f"branch_name{i}",
                                   last_scanned_commit=f"last_scanned_commit{i}"))

    repository_info = RepositoryInfo(project_key="project_key",
                                     repository_id=1,
                                     repository_name="repository_name",
                                     repository_url="https://repository.url",
                                     vcs_instance=1,
                                     branches_info=branches)
    secret_scanner = SecretScanner(
        gitleaks_binary_path="/tmp/gitleaks",
        gitleaks_rules_path="/rules.toml",
        rule_pack_version="0.0.1",
        output_plugin=RESTAPIWriter(rws_url=rws_url),
        repository_info=repository_info,
        username=username,
        personal_access_token=personal_access_token,
    )

    result = secret_scanner.clone_repo(branches[0].branch_name)
    assert result == f"./{repository_info.repository_name}@{branches[0].branch_name}"

    url = repository_info.repository_url.replace("https://", "")
    expected_repo_clone_path = f"{secret_scanner._scan_tmp_directory}/{repository_info.repository_name}@" \
                               f"{branches[0].branch_name}"
    expected_repo_clone_url = f"https://{username}:{personal_access_token}@{url}"
    clone_from.assert_called_once()
    clone_from.assert_called_once_with(expected_repo_clone_url, expected_repo_clone_path,
                                       branch=branches[0].branch_name)


@patch("repository_scanners.secret_scanners.gitleaks_wrapper.GitLeaksWrapper.start_scan")
def test_scan_repo(start_scan):
    start_scan.return_value = None
    rws_url = "https://fakeurl.com:8000"
    username = "username"
    personal_access_token = "personal_access_token"
    branches = []
    for i in range(1, 6):
        branches.append(BranchInfo(branch_id=i,
                                   branch_name=f"branch_name{i}",
                                   last_scanned_commit=f"last_scanned_commit{i}"))

    repository_info = RepositoryInfo(project_key="project_key",
                                     repository_id=1,
                                     repository_name="repository_name",
                                     repository_url="https://repository.url",
                                     vcs_instance=1,
                                     branches_info=branches)
    secret_scanner = SecretScanner(
        gitleaks_binary_path="/tmp/gitleaks",
        gitleaks_rules_path="/rules.toml",
        rule_pack_version="0.0.1",
        output_plugin=RESTAPIWriter(rws_url=rws_url),
        repository_info=repository_info,
        username=username,
        personal_access_token=personal_access_token,
    )
    repo_clone_path = f"{secret_scanner._scan_tmp_directory}/{repository_info.repository_name}@" \
                      f"{branches[0].branch_name}"
    result = secret_scanner.scan_repo(ScanType.BASE, branches[0].branch_name, branches[0].last_scanned_commit,
                                      repo_clone_path)
    assert result is None
    start_scan.assert_called_once()
