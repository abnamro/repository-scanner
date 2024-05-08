# Standard Library
import os
from pathlib import Path
from typing import List
from unittest.mock import patch

# Third Party
import pytest
import yaml

# First Party
from resc_helm_wizard.common import (
    create_helm_values_yaml,
    create_storage_for_db_and_rabbitmq,
    download_rule_toml_file,
    generate_pvc_path,
    get_operating_system,
    get_scheme_host_port_from_url,
    get_vcs_instance_question_answers,
    prepare_vcs_instances_for_helm_values,
    run_deployment_as_per_user_confirmation,
)
from resc_helm_wizard.helm_value import HelmValue
from resc_helm_wizard.vcs_instance import VcsInstance

THIS_DIR = Path(__file__).parent


def test_get_operating_system_windows():
    operating_system = get_operating_system(user_input="Microsoft Windows")
    assert operating_system == "windows"


def test_get_operating_system_linux():
    operating_system = get_operating_system(user_input="Linux")
    assert operating_system == "linux"


def test_get_scheme_host_port_from_url():
    scheme, hostname, port = get_scheme_host_port_from_url(
        url="https://github.com/username/repo1"
    )
    assert scheme == "https"
    assert hostname == "github.com"
    assert port == "443"

    scheme, hostname, port = get_scheme_host_port_from_url(
        url="http://bitbucket.com:9999"
    )
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
        scope=["repo1", "repo2"],
    )

    vcs_instances: List[VcsInstance] = [vcs_instance1]
    helm_values = HelmValue(
        operating_system="linux",
        db_password="dummy_pass",
        db_storage_path="/temp/db",
        rabbitmq_storage_path="/temp/rabbitmq",
        vcs_instances=vcs_instances,
    )
    output_vcs_instances = prepare_vcs_instances_for_helm_values(
        helm_values=helm_values
    )
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
    pvc_path_db_linux_with_skip_create_dir = generate_pvc_path(
        operating_system="linux", path="/tmp", tool_type="database", create_dir=False
    )
    assert pvc_path_db_linux_with_skip_create_dir == "/tmp/resc-db-storage"

    pvc_path_rabbitmq_linux_with_skip_create_dir = generate_pvc_path(
        operating_system="linux", path="/tmp", tool_type="rabbitmq", create_dir=False
    )
    assert pvc_path_rabbitmq_linux_with_skip_create_dir == "/tmp/resc-rabbitmq-storage"

    pvc_path_db_windows_with_skip_create_dir = generate_pvc_path(
        operating_system="windows",
        path="C:/Users/user1/resc",
        tool_type="database",
        create_dir=False,
    )
    assert (
        pvc_path_db_windows_with_skip_create_dir
        == "/run/desktop/mnt/host/c/Users/user1/resc/resc-db-storage"
    )

    pvc_path_rabbitmq_windows_with_skip_create_dir = generate_pvc_path(
        operating_system="windows",
        path="C:/Users/user1/resc",
        tool_type="rabbitmq",
        create_dir=False,
    )
    assert (
        pvc_path_rabbitmq_windows_with_skip_create_dir
        == "/run/desktop/mnt/host/c/Users/user1/resc/"
        "resc-rabbitmq-storage"
    )


@patch("os.path.exists")
@patch("os.makedirs")
@patch("logging.Logger.info")
def test_generate_pvc_path_when_create_dir_true_and_path_exists(
    mock_info_log, mock_make_dir, mock_path_exists
):
    mock_path_exists.return_value = True
    mock_make_dir.return_value = False
    tool_type = "database"
    path = "/tmp"
    expected_call = f"Path already exists. Going to use {path}/resc-db-storage for {tool_type} storage"
    pvc_path = generate_pvc_path(
        operating_system="linux", path="/tmp", tool_type="database", create_dir=True
    )
    assert pvc_path == "/tmp/resc-db-storage"
    mock_info_log.assert_called_once_with(expected_call)


@patch("os.path.exists")
@patch("os.makedirs")
@patch("logging.Logger.info")
def test_generate_pvc_path_when_create_dir_true_and_path_not_exists(
    mock_info_log, mock_make_dir, mock_path_exists
):
    mock_path_exists.return_value = False
    mock_make_dir.return_value = False
    tool_type = "database"
    path = "/tmp"
    expected_call = f"Storage created for {tool_type} at {path}/resc-db-storage"
    pvc_path = generate_pvc_path(
        operating_system="linux", path=path, tool_type=tool_type, create_dir=True
    )
    assert pvc_path == "/tmp/resc-db-storage"
    mock_info_log.assert_called_once_with(expected_call)


@patch("resc_helm_wizard.questions.ask_user_to_select_vcs_instance")
@patch("logging.Logger.error")
def test_get_vcs_instance_question_answers_when_no_vcs_instance_is_selected(
    mock_error_log, mock_ask_user_to_select_vcs_instance
):
    mock_ask_user_to_select_vcs_instance.return_value = None
    with pytest.raises(SystemExit) as excinfo:
        get_vcs_instance_question_answers()
    expected_call = "Aborting the program! No VCS instance was selected"
    mock_error_log.assert_called_once_with(expected_call)
    assert excinfo.value.code == 1


@patch("resc_helm_wizard.questions.ask_user_to_select_vcs_instance")
@patch("resc_helm_wizard.questions.ask_vcs_instance_details")
@patch("resc_helm_wizard.questions.ask_which_github_accounts_to_scan")
def test_get_vcs_instance_question_answers(
    mock_ask_which_github_accounts_to_scan,
    mock_ask_vcs_instance_details,
    mock_ask_user_to_select_vcs_instance,
):
    vcs_instance_info = {
        "url": "https://vcs.com:443",
        "organization": "dummy_org",
        "username": "dummy_user",
        "token": "dummy_token",
    }
    mock_ask_user_to_select_vcs_instance.return_value = [
        "GitHub",
        "Azure Devops",
        "Bitbucket",
    ]
    mock_ask_vcs_instance_details.return_value = vcs_instance_info
    mock_ask_which_github_accounts_to_scan.return_value = (
        "dummy_user, kubernetes, docker"
    )
    github_account_list = [
        account.strip()
        for account in mock_ask_which_github_accounts_to_scan.return_value.split(",")
    ]

    vcs_instances = get_vcs_instance_question_answers()
    assert len(vcs_instances) == 3
    assert vcs_instances[0].host == "vcs.com"
    assert vcs_instances[0].organization == "dummy_org"
    assert vcs_instances[0].password == "dummy_token"
    assert vcs_instances[0].port == "443"
    assert vcs_instances[0].provider_type == "GITHUB_PUBLIC"
    assert vcs_instances[0].scheme == "https"
    assert vcs_instances[0].scope == github_account_list
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


@patch("resc_helm_wizard.questions.ask_local_storage_path")
@patch("os.path.exists")
@patch("resc_helm_wizard.common.generate_pvc_path")
@patch("resc_helm_wizard.common.generate_pvc_path")
def test_create_storage_for_db_and_rabbitmq_where_path_exists(
    mock_rabbitmq_storage_path,
    mock_db_storage_path,
    mock_path_exists,
    mock_local_storage_path,
):
    mock_local_storage_path.return_value = "/tmp"
    mock_path_exists.return_value = True
    mock_rabbitmq_storage_path.return_value = "/tmp/resc-rabbitmq-storage"
    mock_db_storage_path.return_value = "/tmp/resc-db-storage"
    storage_path = create_storage_for_db_and_rabbitmq(operating_system="linux")
    assert storage_path["db_storage_path"] == mock_db_storage_path.return_value


@patch("resc_helm_wizard.questions.ask_local_storage_path")
@patch("os.path.exists")
@patch("resc_helm_wizard.questions.ask_user_confirmation")
@patch("resc_helm_wizard.common.generate_pvc_path")
@patch("resc_helm_wizard.common.generate_pvc_path")
def test_create_storage_for_db_and_rabbitmq_where_path_does_not_exist_and_dir_confirmation_true(
    mock_rabbitmq_storage_path,
    mock_db_storage_path,
    mock_dir_confirm,
    mock_path_exists,
    mock_local_storage_path,
):
    mock_local_storage_path.return_value = "/tmp"
    mock_path_exists.return_value = False
    mock_dir_confirm.return_value = True
    mock_db_storage_path.return_value = "/tmp/resc-db-storage"
    mock_rabbitmq_storage_path.return_value = "/tmp/resc-rabbitmq-storage"
    storage_path = create_storage_for_db_and_rabbitmq(operating_system="linux")
    assert storage_path["db_storage_path"] == mock_db_storage_path.return_value


@patch("resc_helm_wizard.questions.ask_local_storage_path")
@patch("os.path.exists")
@patch("resc_helm_wizard.questions.ask_user_confirmation")
@patch("logging.Logger.warning")
@patch("resc_helm_wizard.questions.ask_user_confirmation")
@patch("logging.Logger.info")
def test_create_storage_for_db_and_rabbitmq_where_path_does_not_exist_and_dir_confirm_false_and_proceed_confirm_false(
    mock_info_log,
    mock_proceed_confirm,
    mock_warning_log,
    mock_dir_confirm,
    mock_path_exists,
    mock_local_storage_path,
):
    mock_local_storage_path.return_value = "/tmp"
    mock_path_exists.return_value = False
    mock_dir_confirm.return_value = False
    mock_proceed_confirm.return_value = False

    expected_call_warning = (
        "Warning! Please ensure the provided directory exists on the system "
        "where you are running the deployment"
    )
    expected_call_info = "Aborting the program!!"

    with pytest.raises(SystemExit) as excinfo:
        create_storage_for_db_and_rabbitmq(operating_system="linux")
    mock_warning_log.assert_called_once_with(expected_call_warning)
    mock_info_log.assert_called_once_with(expected_call_info)
    assert excinfo.value.code == 1


@patch("resc_helm_wizard.common.read_yaml_file")
@patch("os.path.exists")
def test_create_helm_values_yaml_success(mock_file_path_exists, mock_read_yaml_file):
    vcs_instance1 = VcsInstance(
        provider_type="GITHUB_PUBLIC",
        scheme="https",
        host="dummy_host1.com",
        port="443",
        username="dummy_user",
        password="dummy_pass",
        organization="dummy_org",
        scope=["repo1", "repo2"],
    )

    vcs_instances: List[VcsInstance] = [vcs_instance1]
    helm_values = HelmValue(
        operating_system="linux",
        db_password="dummy_pass",
        db_storage_path="/temp/db",
        rabbitmq_storage_path="/temp/rabbitmq",
        vcs_instances=vcs_instances,
    )

    mock_file_path_exists.return_type = True
    input_file_path = os.path.join(
        THIS_DIR.parent, "resc_helm_wizard", "fixtures", "test-values.yaml"
    )
    with open(input_file_path, "r", encoding="utf-8") as file_in:
        values_dict = yaml.safe_load(file_in)
    mock_read_yaml_file.return_value = values_dict
    generated_file_path = os.path.join(THIS_DIR.parent, "custom-values.yaml")
    output_file_generated = create_helm_values_yaml(
        helm_values=helm_values, input_values_yaml_file=input_file_path
    )
    assert output_file_generated is True
    if os.path.isfile(generated_file_path):
        os.remove(generated_file_path)


@patch("logging.Logger.error")
def test_create_helm_values_sys_exit_when_file_not_exists(mock_error_log):
    input_file_path = os.path.join(
        THIS_DIR.parent, "resc_helm_wizard", "fixtures", "not_exist.yaml"
    )
    expected_error_log = f"Aborting the program! {input_file_path} file was not found"
    with pytest.raises(SystemExit) as excinfo:
        create_helm_values_yaml(
            helm_values=None, input_values_yaml_file=input_file_path
        )
    mock_error_log.assert_called_with(expected_error_log)
    assert excinfo.value.code == 1


@patch("resc_helm_wizard.common.read_yaml_file")
@patch("logging.Logger.error")
def test_create_helm_values_sys_exit_when_key_not_exists(
    mock_error_log, mock_read_yaml_file
):
    helm_values = HelmValue(
        operating_system="linux",
        db_password="dummy_pass",
        db_storage_path="/temp/db",
        rabbitmq_storage_path="/temp/rabbitmq",
        vcs_instances=[],
    )
    input_file_path = os.path.join(
        THIS_DIR.parent, "resc_helm_wizard", "fixtures", "test-invalid-values.yaml"
    )
    with open(input_file_path, "r", encoding="utf-8") as file_in:
        values_dict = yaml.safe_load(file_in)
    mock_read_yaml_file.return_value = values_dict
    expected_error_log = (
        f"Aborting the program! 'resc-database' was missing in {input_file_path}"
    )
    with pytest.raises(SystemExit) as excinfo:
        create_helm_values_yaml(
            helm_values=helm_values, input_values_yaml_file=input_file_path
        )
    mock_error_log.assert_called_with(expected_error_log)
    assert excinfo.value.code == 1


@patch("resc_helm_wizard.questions.ask_ssl_verification")
@patch("requests.get")
@patch("logging.Logger.debug")
def test_download_rule_toml_file_success(
    mock_debug_log, mock_get, mock_ask_ssl_verification_confirm
):
    url = "https://example.com/rule_file.toml"
    file = "temp_file.toml"
    content = b"file content"
    expected_debug_log = f"{file} successfully downloaded"
    mock_ask_ssl_verification_confirm.return_value = True
    mock_get.return_value.status_code = 200
    mock_get.return_value.content = content
    downloaded = download_rule_toml_file(url=url, file=file)
    assert downloaded is True
    mock_debug_log.assert_called_with(expected_debug_log)
    with open(file, "rb") as file_output:
        assert file_output.read() == content
    if os.path.isfile(file):
        os.remove(file)


@patch("resc_helm_wizard.questions.ask_ssl_verification")
@patch("requests.get")
@patch("os.path.exists")
@patch("os.path.getsize")
@patch("logging.Logger.error")
def test_download_rule_toml_file_failure(
    mock_error_log,
    mock_os_path_getsize,
    mock_os_path_exists,
    mock_get,
    mock_ask_ssl_verification_confirm,
):
    url = "https://example.com/rule_file.toml"
    file = "temp_file.toml"
    content = b"file content"
    expected_error_log = "Unable to download the rule file"
    mock_ask_ssl_verification_confirm.return_value = True
    mock_os_path_exists.return_value = False
    mock_os_path_getsize.return_value = -1
    mock_get.return_value.status_code = 500
    mock_get.return_value.content = content
    downloaded = download_rule_toml_file(url=url, file=file)
    assert downloaded is False
    mock_error_log.assert_called_with(expected_error_log)
    with open(file, "rb") as file_output:
        assert file_output.read() == content
    if os.path.isfile(file):
        os.remove(file)


@patch("resc_helm_wizard.questions.ask_user_confirmation")
@patch("resc_helm_wizard.common.run_deployment")
def test_run_deployment_as_per_user_confirmation_yes(
    mock_run_deployment, mock_ask_user_confirmation
):
    run_deployment_confirm_msg = "Do you want to run deployment?"
    mock_ask_user_confirmation.return_value = True
    mock_run_deployment.return_value = True
    deployment_status = run_deployment_as_per_user_confirmation()
    assert deployment_status is None
    mock_run_deployment.assert_called_once_with
    mock_ask_user_confirmation.assert_called_once_with(msg=run_deployment_confirm_msg)


@patch("resc_helm_wizard.questions.ask_user_confirmation")
@patch("logging.Logger.info")
def test_run_deployment_as_per_user_confirmation_no(
    mock_log_info, mock_ask_user_confirmation
):
    expected_info_log = "Skipping deployment..."
    run_deployment_confirm_msg = "Do you want to run deployment?"
    mock_ask_user_confirmation.return_value = False
    deployment_status = run_deployment_as_per_user_confirmation()
    assert deployment_status is None
    mock_ask_user_confirmation.assert_called_once_with(msg=run_deployment_confirm_msg)
    mock_log_info.assert_called_with(expected_info_log)
