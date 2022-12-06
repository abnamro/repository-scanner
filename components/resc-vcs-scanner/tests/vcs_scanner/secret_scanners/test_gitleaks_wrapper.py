# Standard Library
import sys

# Third Party
from _pytest.monkeypatch import MonkeyPatch

# First Party
from vcs_scanner.constants import LEAKS_FOUND_EXIT_CODE
from vcs_scanner.secret_scanners.gitleaks_wrapper import GitLeaksWrapper

sys.path.insert(0, "src")

mp = MonkeyPatch()
mp.setenv('GITLEAKS_PATH', 'fake_gitleaks_path')
mp.setenv('RESC_RABBITMQ_SERVICE_HOST', 'fake-rabbitmq-host.fakehost.com')
mp.setenv('RABBITMQ_DEFAULT_VHOST', 'vhost')
mp.setenv('RESC_API_NO_AUTH_SERVICE_HOST', 'fake_api_service_host')
mp.setenv('RABBITMQ_USERNAME', 'fake user')
mp.setenv('RABBITMQ_PASSWORD', 'fake pass')
mp.setenv('RABBITMQ_QUEUE', 'queuename')

BITBUCKET_USERNAME = "test"
GITLEAKS_PATH = "gitleaks_exec"


def test_repository_scanner_calculate_permanent_leak_url():
    leak_url = 'https://bitbucket.com:1234/scm/ups/thisismyrepo.git/blob/' \
               '123123123123123123123123123123/path/to/the/file.json#L1337'
    commit_id = '123123123123123123123123123123'
    repo = 'thisismyrepo.git'

    leak_permalink = GitLeaksWrapper._calculate_permanent_leak_url(leak_url,
                                                                   repo,
                                                                   commit_id)
    assert leak_permalink == 'https://bitbucket.com:1234/projects/ups/repos/thisismyrepo/commits/' \
                             '123123123123123123123123123123#path/to/the/file.json'


def test_repository_scanner_is_valid_timestamp():
    timestamp_input = '2020-08-07T16:31:11+02:00'
    timestamp_output = GitLeaksWrapper._is_valid_timestamp(timestamp_input)

    assert timestamp_output


def test_repository_scanner_is_valid_timestamp_invalid():
    timestamp_input = '2020-18-07T16:31:11+02:00'
    timestamp_output = GitLeaksWrapper._is_valid_timestamp(timestamp_input)

    assert not timestamp_output


def test_secret_scanner_build_gitleaks_command_with_custom_exit_code():
    scan_from = None
    gitleaks_path = '/usr/bin/gitleaks'
    rules_filepath = '/usr/bin/gitleaks/rules.toml'
    report_filepath = '/tmp'
    repo_clone_path = '/tmp/project1'

    gitleaks_wrapper = GitLeaksWrapper(scan_from=scan_from,
                                       gitleaks_path=gitleaks_path,
                                       repository_path=repo_clone_path,
                                       rules_filepath=rules_filepath,
                                       report_filepath=report_filepath,
                                       )
    gitleaks_command = gitleaks_wrapper._build_gitleaks_command()
    assert gitleaks_command
    assert len(gitleaks_command) == 6
    assert gitleaks_command[0] == gitleaks_path
    assert f"--source={repo_clone_path}" in gitleaks_command
    assert f"--config={rules_filepath}" in gitleaks_command
    assert f"--report-path={report_filepath}" in gitleaks_command
    assert f"--exit-code={LEAKS_FOUND_EXIT_CODE}" in gitleaks_command


def test_secret_scanner_build_gitleaks_command_for_non_git_scan():
    scan_from = None
    gitleaks_path = '/usr/bin/gitleaks'
    rules_filepath = '/usr/bin/gitleaks/rules.toml'
    report_filepath = '/tmp'
    repo_clone_path = '/tmp/project1'
    git_scan = False

    gitleaks_wrapper = GitLeaksWrapper(scan_from=scan_from,
                                       gitleaks_path=gitleaks_path,
                                       repository_path=repo_clone_path,
                                       rules_filepath=rules_filepath,
                                       report_filepath=report_filepath,
                                       git_scan=git_scan
                                       )
    gitleaks_command = gitleaks_wrapper._build_gitleaks_command()
    assert gitleaks_command
    assert len(gitleaks_command) == 7
    assert gitleaks_command[0] == gitleaks_path
    assert f"--source={repo_clone_path}" in gitleaks_command
    assert f"--config={rules_filepath}" in gitleaks_command
    assert f"--report-path={report_filepath}" in gitleaks_command
    assert f"--exit-code={LEAKS_FOUND_EXIT_CODE}" in gitleaks_command
    assert "--no-git" in gitleaks_command


def test_secret_scanner_build_gitleaks_command_for_base_scan():
    scan_from = None
    gitleaks_path = '/usr/bin/gitleaks'
    rules_filepath = '/usr/bin/gitleaks/rules.toml'
    report_filepath = '/tmp'
    repo_clone_path = '/tmp/project1'

    gitleaks_wrapper = GitLeaksWrapper(scan_from=scan_from,
                                       gitleaks_path=gitleaks_path,
                                       repository_path=repo_clone_path,
                                       rules_filepath=rules_filepath,
                                       report_filepath=report_filepath
                                       )
    gitleaks_command = gitleaks_wrapper._build_gitleaks_command()
    assert gitleaks_command
    assert len(gitleaks_command) == 6
    assert gitleaks_command[0] == gitleaks_path
    assert f"--source={repo_clone_path}" in gitleaks_command
    assert f"--config={rules_filepath}" in gitleaks_command
    assert f"--report-path={report_filepath}" in gitleaks_command
    assert f"--exit-code={LEAKS_FOUND_EXIT_CODE}" in gitleaks_command


def test_secret_scanner_build_gitleaks_command_for_incremental_scan():
    scan_from = 'fake-hash'
    gitleaks_path = '/usr/bin/gitleaks'
    rules_filepath = '/usr/bin/gitleaks/rules.toml'
    report_filepath = '/tmp'
    repo_clone_path = '/tmp/project1'

    gitleaks_wrapper = GitLeaksWrapper(scan_from=scan_from,
                                       gitleaks_path=gitleaks_path,
                                       repository_path=repo_clone_path,
                                       rules_filepath=rules_filepath,
                                       report_filepath=report_filepath
                                       )
    gitleaks_command = gitleaks_wrapper._build_gitleaks_command()
    print(f"gitleaks_command==>{gitleaks_command}")
    assert gitleaks_command
    assert len(gitleaks_command) == 7
    assert gitleaks_command[0] == gitleaks_path
    assert f"--source={repo_clone_path}" in gitleaks_command
    assert f"--config={rules_filepath}" in gitleaks_command
    assert f"--report-path={report_filepath}" in gitleaks_command
    assert f"--exit-code={LEAKS_FOUND_EXIT_CODE}" in gitleaks_command
    assert f"--log-opts={scan_from}.." in gitleaks_command
