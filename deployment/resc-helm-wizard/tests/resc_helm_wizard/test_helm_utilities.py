# Standard Library
import subprocess
import unittest.mock as mock
from unittest.mock import patch

# First Party
from resc_helm_wizard import constants
from resc_helm_wizard.helm_utilities import (
    add_helm_repository,
    check_helm_release_exists,
    get_version_from_downloaded_chart,
    install_or_upgrade_helm_release,
    update_helm_repository,
    validate_helm_deployment_status,
)


@patch("subprocess.check_output")
@patch("logging.Logger.info")
def test_install_or_upgrade_helm_release_success(mock_info_log, mock_check_output):
    expected_output = b"installation successful"
    mock_check_output.return_value = expected_output
    expected_info_log = "installation successful"
    actual_output = install_or_upgrade_helm_release(action="install")
    assert actual_output is True
    mock_info_log.assert_called_with(expected_info_log)


@patch("logging.Logger.error")
def test_install_or_upgrade_helm_release_failure(mock_error_log):
    expected_error_log = f"An error occurred during {constants.CHART_NAME} deployment"
    with mock.patch("subprocess.check_output") as mock_check_output:
        mock_check_output.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd="my command"
        )
        actual_output = install_or_upgrade_helm_release(action="install")
        assert mock_check_output.called
        assert actual_output is False
        mock_error_log.assert_called_with(expected_error_log)


@patch("subprocess.check_output")
def test_get_version_from_downloaded_chart_success(mock_check_output):
    expected_output = (
        b'[{"name":"resc-helm-repo/resc","version":"1.1.0","app_version":"1.1.0",'
        b'"description":"A Helm chart for the Repository Scanner"}]\n'
    )
    mock_check_output.return_value = expected_output
    actual_output = get_version_from_downloaded_chart()
    assert actual_output == "1.1.0"


@patch("subprocess.check_output")
def test_get_version_from_downloaded_chart_failure(mock_check_output):
    expected_output = b"{}"
    mock_check_output.return_value = expected_output
    actual_output = get_version_from_downloaded_chart()
    assert actual_output is None


@patch("subprocess.run")
def test_add_helm_repository_success(mock_check_output):
    cmd = [
        "helm",
        "repo",
        "add",
        constants.HELM_REPO_NAME,
        constants.RESC_HELM_REPO_URL,
        "-n",
        constants.NAMESPACE,
    ]
    add_helm_repository()
    assert mock_check_output.called
    mock_check_output.assert_called_once_with(cmd, check=True)


@patch("logging.Logger.error")
def test_add_helm_repository_failure(mock_error_log):
    cmd = [
        "helm",
        "repo",
        "add",
        constants.HELM_REPO_NAME,
        constants.RESC_HELM_REPO_URL,
        "-n",
        constants.NAMESPACE,
    ]
    expected_error_log = "An error occurred while adding the helm repository"
    with mock.patch("subprocess.run") as mock_check_output, mock.patch(
        "sys.exit"
    ) as mock_sys_exit:
        mock_check_output.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd=cmd
        )
        add_helm_repository()
        assert mock_check_output.called
        mock_error_log.assert_called_with(expected_error_log)
        mock_check_output.assert_called_once_with(cmd, check=True)
        mock_sys_exit.assert_called_once_with(1)


@patch("subprocess.run")
def test_update_helm_repository_success(mock_check_output):
    cmd = ["helm", "repo", "update", "-n", constants.NAMESPACE]
    update_helm_repository()
    assert mock_check_output.called
    mock_check_output.assert_called_once_with(cmd, check=True)


@patch("logging.Logger.error")
def test_update_helm_repository_failure(mock_error_log):
    cmd = ["helm", "repo", "update", "-n", constants.NAMESPACE]
    expected_error_log = "An error occurred while updating the helm repository"
    with mock.patch("subprocess.run") as mock_check_output, mock.patch(
        "sys.exit"
    ) as mock_sys_exit:
        mock_check_output.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd=cmd
        )
        update_helm_repository()
        assert mock_check_output.called
        mock_error_log.assert_called_with(expected_error_log)
        mock_check_output.assert_called_once_with(cmd, check=True)
        mock_sys_exit.assert_called_once_with(1)


@patch("subprocess.run")
@patch("logging.Logger.info")
def test_validate_helm_deployment_status_success(mock_info_log, mock_check_output):
    cmd = ["helm", "status", constants.RELEASE_NAME, "-n", constants.NAMESPACE]
    expected_output = "RELEASE STATUS: deployed"
    expected_info_log = (
        "Refer this link for more information on how to trigger the scan: "
        "https://github.com/abnamro/repository-scanner/tree/main/deployment/kubernetes#trigger-scanning"
    )
    mock_check_output.return_value.stdout = expected_output
    validate_helm_deployment_status()
    assert mock_check_output.called
    mock_check_output.assert_called_once_with(
        cmd, capture_output=True, check=True, text=True
    )
    mock_info_log.assert_called_with(expected_info_log)


@patch("logging.Logger.error")
def test_validate_helm_deployment_status_failure(mock_error_log):
    cmd = ["helm", "status", constants.RELEASE_NAME, "-n", constants.NAMESPACE]
    expected_error_log = (
        "An error occurred during deployment. Please run this command to debug any issue: "
        "kubectl get pods -n resc"
    )
    with mock.patch("subprocess.run") as mock_check_output, mock.patch(
        "sys.exit"
    ) as mock_sys_exit:
        mock_check_output.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd=cmd
        )
        validate_helm_deployment_status()
        assert mock_check_output.called
        mock_error_log.assert_called_with(expected_error_log)
        mock_check_output.assert_called_once_with(
            cmd, capture_output=True, check=True, text=True
        )
        mock_sys_exit.assert_called_once_with(1)


@patch("subprocess.run")
def test_check_helm_release_exists_true(mock_check_output):
    cmd = ["helm", "list", "-f", constants.RELEASE_NAME, "-n", constants.NAMESPACE]
    expected_output = f"NAME: {constants.RELEASE_NAME}"
    mock_check_output.return_value.stdout = expected_output
    release_exists = check_helm_release_exists()
    assert mock_check_output.called
    mock_check_output.assert_called_once_with(
        cmd, capture_output=True, text=True, check=True
    )
    assert release_exists is True


@patch("subprocess.run")
def test_check_helm_release_exists_false(mock_check_output):
    cmd = ["helm", "list", "-f", constants.RELEASE_NAME, "-n", constants.NAMESPACE]
    expected_output = "NAME NAMESPACE REVISION UPDATED STATUS CHART APP VERSION"
    mock_check_output.return_value.stdout = expected_output
    release_exists = check_helm_release_exists()
    assert mock_check_output.called
    mock_check_output.assert_called_once_with(
        cmd, capture_output=True, text=True, check=True
    )
    assert release_exists is False
