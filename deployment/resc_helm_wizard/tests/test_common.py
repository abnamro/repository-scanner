# Standard Library
import os
import sys
from pathlib import Path
from typing import List
from unittest.mock import patch

# Third Party
import pytest

# First Party
from common import (
    create_helm_values_yaml,
    create_storage_for_db_and_rabbitmq,
    generate_pvc_path,
    get_operating_system,
    get_scheme_host_port_from_url,
    get_vcs_instance_question_answers,
    prepare_vcs_instances_for_helm_values
)
from helm_value import HelmValue
from vcs_instance import VcsInstance

sys.path.insert(0, "src")

THIS_DIR = Path(__file__).parent


def test_get_operating_system_windows():
    operating_system = get_operating_system(user_input="Microsoft Windows")
    assert operating_system == "windows"


def test_get_operating_system_linux():
    operating_system = get_operating_system(user_input="Linux")
    assert operating_system == "linux"


def test_get_scheme_host_port_from_url():
    scheme, hostname, port = get_scheme_host_port_from_url(url="https://github.com/username/repo1")
    assert scheme == "https"
    assert hostname == "github.com"
    assert port == "443"

    scheme, hostname, port = get_scheme_host_port_from_url(url="http://bitbucket.com:9999")
    assert scheme == "http"
    assert hostname == "bitbucket.com"
    assert port == "9999"


def test_prepare_vcs_instances_for_helm_values():
    vcs_instance1 = VcsInstance(
        provider_type="GITHUB_PUBLIC",
        scheme="https",
        host="dummy_host1.com",
        port="443",
        username="dummy_user",
        password="dummy_pass",
        organization="dummy_org",
        scope=["repo1", "repo2"])

    vcs_instances: List[VcsInstance] = [vcs_instance1]
    helm_values = HelmValue(
        operating_system="linux",
        db_password="dummy_pass",
        db_storage_path="/temp/db",
        rabbitmq_storage_path="/temp/rabbitmq",
        vcs_instances=vcs_instances
    )
    output_vcs_instances = prepare_vcs_instances_for_helm_values(helm_values=helm_values)
    assert output_vcs_instances[0]["name"] == "GITHUB_PUBLIC"
    assert output_vcs_instances[0]["scope"] == ["repo1", "repo2"]
    assert output_vcs_instances[0]["hostname"] == "dummy_host1.com"
    assert output_vcs_instances[0]["port"] == "443"
    assert output_vcs_instances[0]["scheme"] == "https"
    assert output_vcs_instances[0]["username"] == "GITHUB_PUBLIC_USERNAME"
    assert output_vcs_instances[0]["usernameValue"] == "dummy_user"
    assert output_vcs_instances[0]["token"] == "GITHUB_PUBLIC_TOKEN"
    assert output_vcs_instances[0]["tokenValue"] == "dummy_pass"
    assert output_vcs_instances[0]["organization"] == "dummy_org"


def test_generate_pvc_path_when_create_dir_false():
    pvc_path_db_linux_with_skip_create_dir = generate_pvc_path(operating_system="linux", path="/tmp",
                                                               tool_type="database", create_dir=False)
    assert pvc_path_db_linux_with_skip_create_dir == "/tmp/resc-db-storage"

    pvc_path_rabbitmq_linux_with_skip_create_dir = generate_pvc_path(operating_system="linux", path="/tmp",
                                                                     tool_type="rabbitmq", create_dir=False)
    assert pvc_path_rabbitmq_linux_with_skip_create_dir == "/tmp/resc-rabbitmq-storage"

    pvc_path_db_windows_with_skip_create_dir = generate_pvc_path(operating_system="windows", path="C:/Users/user1/resc",
                                                                 tool_type="database", create_dir=False)
    assert pvc_path_db_windows_with_skip_create_dir == "/run/desktop/mnt/host/c/Users/user1/resc/resc-db-storage"

    pvc_path_rabbitmq_windows_with_skip_create_dir = generate_pvc_path(operating_system="windows",
                                                                       path="C:/Users/user1/resc",
                                                                       tool_type="rabbitmq", create_dir=False)
    assert pvc_path_rabbitmq_windows_with_skip_create_dir == "/run/desktop/mnt/host/c/Users/user1/resc/" \
                                                             "resc-rabbitmq-storage"


@patch("os.path.exists")
@patch("os.makedirs")
@patch("logging.Logger.info")
def test_generate_pvc_path_when_create_dir_true_and_path_exists(mock_info_log, mock_make_dir, mock_path_exists):
    mock_path_exists.return_value = True
    mock_make_dir.return_value = False
    tool_type = "database"
    path = "/tmp"
    expected_call = f"Path already exists. Going to use {path}/resc-db-storage for {tool_type} storage"
    pvc_path = generate_pvc_path(operating_system="linux", path="/tmp",
                                 tool_type="database", create_dir=True)
    assert pvc_path == "/tmp/resc-db-storage"
    mock_info_log.assert_called_once_with(expected_call)


@patch("os.path.exists")
@patch("os.makedirs")
@patch("logging.Logger.info")
def test_generate_pvc_path_when_create_dir_true_and_path_not_exists(mock_info_log, mock_make_dir, mock_path_exists):
    mock_path_exists.return_value = False
    mock_make_dir.return_value = False
    tool_type = "database"
    path = "/tmp"
    expected_call = f"Storage created for {tool_type} at {path}/resc-db-storage"
    pvc_path = generate_pvc_path(operating_system="linux", path=path,
                                 tool_type=tool_type, create_dir=True)
    assert pvc_path == "/tmp/resc-db-storage"
    mock_info_log.assert_called_once_with(expected_call)


@patch("questions.ask_user_to_select_vcs_instance")
@patch("logging.Logger.error")
def test_get_vcs_instance_question_answers_when_no_vcs_instance_is_selected(mock_error_log,
                                                                            mock_ask_user_to_select_vcs_instance):
    mock_ask_user_to_select_vcs_instance.return_value = None
    with pytest.raises(SystemExit) as excinfo:
        get_vcs_instance_question_answers()
    expected_call = "Aborting the program! No VCS instance was selected"
    mock_error_log.assert_called_once_with(expected_call)
    assert excinfo.value.code is None


@patch("questions.ask_user_to_select_vcs_instance")
@patch("questions.ask_vcs_instance_details")
def test_get_vcs_instance_question_answers(mock_ask_vcs_instance_details,
                                           mock_ask_user_to_select_vcs_instance,
                                           ):
    vcs_instance_info = {"url": "https://vcs.com:443", "organization": "dummy_org", "username": "dummy_user",
                         "token": "dummy_token"}
    mock_ask_user_to_select_vcs_instance.return_value = ["GitHub", "Azure Devops", "Bitbucket"]
    mock_ask_vcs_instance_details.return_value = vcs_instance_info

    vcs_instances = get_vcs_instance_question_answers()
    assert len(vcs_instances) == 3
    assert vcs_instances[0].host == "vcs.com"
    assert vcs_instances[0].organization == "dummy_org"
    assert vcs_instances[0].password == "dummy_token"
    assert vcs_instances[0].port == "443"
    assert vcs_instances[0].provider_type == "GITHUB_PUBLIC"
    assert vcs_instances[0].scheme == "https"
    assert vcs_instances[0].scope == ["kubernetes", "docker"]
    assert vcs_instances[0].username == "dummy_user"

    assert vcs_instances[1].host == "vcs.com"
    assert vcs_instances[1].organization == "dummy_org"
    assert vcs_instances[1].password == "dummy_token"
    assert vcs_instances[1].port == "443"
    assert vcs_instances[1].provider_type == "AZURE_DEVOPS"
    assert vcs_instances[1].scheme == "https"
    assert vcs_instances[1].scope == []
    assert vcs_instances[1].username == "dummy_user"

    assert vcs_instances[2].host == "vcs.com"
    assert vcs_instances[2].organization == "dummy_org"
    assert vcs_instances[2].password == "dummy_token"
    assert vcs_instances[2].port == "443"
    assert vcs_instances[2].provider_type == "BITBUCKET"
    assert vcs_instances[2].scheme == "https"
    assert vcs_instances[2].scope == []
    assert vcs_instances[2].username == "dummy_user"


@patch("questions.ask_local_storage_path")
@patch("os.path.exists")
@patch("common.generate_pvc_path")
@patch("common.generate_pvc_path")
def test_create_storage_for_db_and_rabbitmq_where_path_exists(mock_rabbitmq_storage_path,
                                                              mock_db_storage_path, mock_path_exists,
                                                              mock_local_storage_path):
    mock_local_storage_path.return_value = "/tmp"
    mock_path_exists.return_value = True
    mock_rabbitmq_storage_path.return_value = "/tmp/resc-rabbitmq-storage"
    mock_db_storage_path.return_value = "/tmp/resc-db-storage"
    storage_path = create_storage_for_db_and_rabbitmq(operating_system="linux")
    assert storage_path["db_storage_path"] == mock_db_storage_path.return_value


@patch("questions.ask_local_storage_path")
@patch("os.path.exists")
@patch("questions.ask_user_confirmation")
@patch("common.generate_pvc_path")
@patch("common.generate_pvc_path")
def test_create_storage_for_db_and_rabbitmq_where_path_does_not_exist_and_dir_confirmation_true(
        mock_rabbitmq_storage_path,
        mock_db_storage_path, mock_dir_confirm,
        mock_path_exists, mock_local_storage_path):
    mock_local_storage_path.return_value = "/tmp"
    mock_path_exists.return_value = False
    mock_dir_confirm.return_value = True
    mock_db_storage_path.return_value = "/tmp/resc-db-storage"
    mock_rabbitmq_storage_path.return_value = "/tmp/resc-rabbitmq-storage"
    storage_path = create_storage_for_db_and_rabbitmq(operating_system="linux")
    assert storage_path["db_storage_path"] == mock_db_storage_path.return_value


@patch("questions.ask_local_storage_path")
@patch("os.path.exists")
@patch("questions.ask_user_confirmation")
@patch("logging.Logger.warning")
@patch("questions.ask_user_confirmation")
@patch("logging.Logger.info")
def test_create_storage_for_db_and_rabbitmq_where_path_does_not_exist_and_dir_confirm_false_and_proceed_confirm_false(
        mock_info_log,
        mock_proceed_confirm,
        mock_warning_log,
        mock_dir_confirm,
        mock_path_exists,
        mock_local_storage_path):
    mock_local_storage_path.return_value = "/tmp"
    mock_path_exists.return_value = False
    mock_dir_confirm.return_value = False
    mock_proceed_confirm.return_value = False

    expected_call_warning = "Warning! Please ensure the provided directory exists on the system " \
                            "where you are running the deployment"
    expected_call_info = "Aborting the program!!"

    with pytest.raises(SystemExit) as excinfo:
        create_storage_for_db_and_rabbitmq(operating_system="linux")
    mock_warning_log.assert_called_once_with(expected_call_warning)
    mock_info_log.assert_called_once_with(expected_call_info)
    assert excinfo.value.code is None


@patch("os.path.exists")
@patch("logging.Logger.info")
def test_create_helm_values_yaml_success(
        mock_info_log,
        mock_file_path_exists):
    vcs_instance1 = VcsInstance(
        provider_type="GITHUB_PUBLIC",
        scheme="https",
        host="dummy_host1.com",
        port="443",
        username="dummy_user",
        password="dummy_pass",
        organization="dummy_org",
        scope=["repo1", "repo2"])

    vcs_instances: List[VcsInstance] = [vcs_instance1]
    helm_values = HelmValue(
        operating_system="linux",
        db_password="dummy_pass",
        db_storage_path="/temp/db",
        rabbitmq_storage_path="/temp/rabbitmq",
        vcs_instances=vcs_instances
    )
    mock_file_path_exists.return_type = True
    helm_deployment_help_link = "https://github.com/abnamro/repository-scanner/" \
                                "blob/main/deployment/kubernetes/README.md"
    input_file_path = os.path.join(THIS_DIR.parent, "tests", "fixtures", "test-values.yaml")
    generated_file_path = os.path.join(THIS_DIR.parent, "custom-values.yaml")
    expected_info_log = f"Helm values yaml file has been successfully generated at {generated_file_path}. " \
                        "Please refer this link to continue with the deployment or " \
                        f"to make any customizations: {helm_deployment_help_link}"
    create_helm_values_yaml(helm_values=helm_values, input_values_yaml_file=input_file_path)
    mock_info_log.assert_called_with(expected_info_log)
    if os.path.exists(generated_file_path):
        os.remove(generated_file_path)


@patch("logging.Logger.error")
def test_create_helm_values_sys_exit_when_file_not_exists(mock_error_log):
    input_file_path = os.path.join(THIS_DIR.parent, "tests", "fixtures", "not_exist.yaml")
    expected_error_log = f"Aborting the program! {input_file_path} file was not found"
    with pytest.raises(SystemExit) as excinfo:
        create_helm_values_yaml(helm_values=None, input_values_yaml_file=input_file_path)
    mock_error_log.assert_called_with(expected_error_log)
    assert excinfo.value.code is None


@patch("logging.Logger.error")
def test_create_helm_values_sys_exit_when_key_not_exists(mock_error_log):
    helm_values = HelmValue(
        operating_system="linux",
        db_password="dummy_pass",
        db_storage_path="/temp/db",
        rabbitmq_storage_path="/temp/rabbitmq",
        vcs_instances=[]
    )
    input_file_path = os.path.join(THIS_DIR.parent, "tests", "fixtures", "test-invalid-values.yaml")
    expected_error_log = f"Aborting the program! 'resc-database' was missing in {input_file_path}"
    with pytest.raises(SystemExit) as excinfo:
        create_helm_values_yaml(helm_values=helm_values, input_values_yaml_file=input_file_path)
    mock_error_log.assert_called_with(expected_error_log)
    assert excinfo.value.code is None
