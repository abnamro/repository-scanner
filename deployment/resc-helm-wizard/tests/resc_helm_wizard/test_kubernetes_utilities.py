# Standard Library
import subprocess
from unittest.mock import patch

# First Party
from resc_helm_wizard.kubernetes_utilities import create_namespace_if_not_exists


@patch("subprocess.run")
@patch("subprocess.run")
@patch("logging.Logger.info")
def test_create_namespace_if_not_exists_failure(
    mock_info_log, mock_subprocess_create_namespace, mock_subprocess_get_namespace
):
    namespace_name = "test-namespace"
    get_namespace_cmd = ["kubectl", "get", "namespace", namespace_name]
    create_namespace_cmd = ["kubectl", "create", "namespace", namespace_name]

    mock_subprocess_get_namespace.return_value = subprocess.CompletedProcess(
        args=get_namespace_cmd,
        returncode=0,
        stdout="",
        stderr='namespaces "test-namespace" ' "already exists",
    )

    mock_subprocess_create_namespace.return_value = subprocess.CompletedProcess(
        args=create_namespace_cmd, returncode=0, stdout=None, stderr=None
    )

    expected_info_log = (
        f"Namespace {namespace_name} already exists. Preparing for deployment..."
    )

    created = create_namespace_if_not_exists(namespace_name=namespace_name)
    assert mock_subprocess_get_namespace.called
    mock_subprocess_get_namespace.assert_called_once_with(
        get_namespace_cmd, capture_output=True, text=True, check=False
    )
    assert created is True
    mock_info_log.assert_called_with(expected_info_log)


@patch("subprocess.run")
@patch("subprocess.run")
@patch("logging.Logger.error")
def test_create_namespace_if_not_exists_when_namespace_already_present(
    mock_error_log, mock_subprocess_create_namespace, mock_subprocess_get_namespace
):
    namespace_name = "test-namespace"
    get_namespace_cmd = ["kubectl", "get", "namespace", namespace_name]
    create_namespace_cmd = ["kubectl", "create", "namespace", namespace_name]

    mock_subprocess_get_namespace.return_value = subprocess.CompletedProcess(
        args=get_namespace_cmd,
        returncode=1,
        stdout="",
        stderr="Error from server (NotFound):"
        ' namespaces "test-namespace" '
        "not found",
    )

    mock_subprocess_create_namespace.return_value = subprocess.CompletedProcess(
        args=create_namespace_cmd, returncode=0, stdout=None, stderr=None
    )

    expected_error_log = (
        f"Error reading namespace: {namespace_name}. Aborting deployment..."
    )

    created = create_namespace_if_not_exists(namespace_name=namespace_name)
    assert mock_subprocess_get_namespace.called
    assert created is False
    mock_error_log.assert_called_with(expected_error_log)


@patch("subprocess.run")
@patch("subprocess.run")
@patch("logging.Logger.info")
def test_create_namespace_if_not_exists_when_namespace_not_present(
    mock_info_log, mock_subprocess_create_namespace, mock_subprocess_get_namespace
):
    namespace_name = "test-namespace"
    get_namespace_cmd = ["kubectl", "get", "namespace", namespace_name]
    create_namespace_cmd = ["kubectl", "create", "namespace", namespace_name]

    mock_subprocess_get_namespace.return_value = subprocess.CompletedProcess(
        args=get_namespace_cmd,
        returncode=0,
        stdout="",
        stderr="Error from server (NotFound):"
        ' namespaces "test-namespace" '
        "not found",
    )

    mock_subprocess_create_namespace.return_value = subprocess.CompletedProcess(
        args=create_namespace_cmd, returncode=0, stdout=None, stderr=None
    )

    expected_info_log = (
        f"Namespace {namespace_name} created. Preparing for deployment..."
    )

    created = create_namespace_if_not_exists(namespace_name=namespace_name)
    assert mock_subprocess_get_namespace.called
    assert created is True
    mock_info_log.assert_called_with(expected_info_log)
