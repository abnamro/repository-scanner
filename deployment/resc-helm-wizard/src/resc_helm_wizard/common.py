# Standard Library
import logging
import os
import sys
from typing import List
from urllib.parse import urlparse

# Third Party
import pkg_resources
import requests
import yaml

# First Party
from resc_helm_wizard import constants, questions
from resc_helm_wizard.helm_utilities import (
    add_helm_repository,
    check_helm_release_exists,
    install_or_upgrade_helm_release,
    update_helm_repository,
    validate_helm_deployment_status,
)
from resc_helm_wizard.helm_value import HelmValue
from resc_helm_wizard.kubernetes_utilities import create_namespace_if_not_exists
from resc_helm_wizard.vcs_instance import VcsInstance

logging.basicConfig(level=logging.INFO)


def get_operating_system(user_input: str) -> str:
    """
        Retrieve operating system
    :param user_input:
        input from user
    :return: str
        Returns windows or linux based on the user input
    """
    if user_input == "Microsoft Windows":
        operating_system = "windows"
    else:
        operating_system = "linux"
    return operating_system


def create_storage_for_db_and_rabbitmq(operating_system: str) -> dict:
    """
        Creates volume storage for database and rabbitmq
    :param operating_system:
        operating system
    :return: dict
        Returns dictionary containing database storage and rabbitmq storage path
    """
    local_storage = questions.ask_local_storage_path()

    if os.path.exists(local_storage):
        db_storage_path = generate_pvc_path(
            operating_system=operating_system,
            path=local_storage,
            tool_type="database",
            create_dir=True,
        )
        rabbitmq_storage_path = generate_pvc_path(
            operating_system=operating_system,
            path=local_storage,
            tool_type="rabbitmq",
            create_dir=True,
        )
    else:
        dir_confirm_msg = f"Do you want to create the directory {local_storage}?"
        dir_confirm = questions.ask_user_confirmation(msg=dir_confirm_msg)
        if dir_confirm is True:
            db_storage_path = generate_pvc_path(
                operating_system=operating_system,
                path=local_storage,
                tool_type="database",
                create_dir=True,
            )
            rabbitmq_storage_path = generate_pvc_path(
                operating_system=operating_system,
                path=local_storage,
                tool_type="rabbitmq",
                create_dir=True,
            )
        else:
            logging.warning(
                "Warning! Please ensure the provided directory exists on the system where you are running the "
                "deployment"
            )
            proceed_confirm = questions.ask_user_confirmation(
                msg="Are you sure you want to proceed?"
            )
            if proceed_confirm is True:
                db_storage_path = generate_pvc_path(
                    operating_system=operating_system,
                    path=local_storage,
                    tool_type="database",
                    create_dir=False,
                )
                rabbitmq_storage_path = generate_pvc_path(
                    operating_system=operating_system,
                    path=local_storage,
                    tool_type="rabbitmq",
                    create_dir=False,
                )
            else:
                logging.info("Aborting the program!!")
                sys.exit(1)
    storage_path = {
        "db_storage_path": db_storage_path,
        "rabbitmq_storage_path": rabbitmq_storage_path,
    }
    return storage_path


def generate_pvc_path(
    operating_system: str, path: str, tool_type: str, create_dir: bool
) -> str:
    """
        Generates volume claim path for database and rabbitmq
    :param operating_system:
        operating system
    :param path:
        path provided by user
    :param tool_type:
        tool type either database or rabbitmq
    :param create_dir:
        should create directory or not
    :return: str
        Returns volume claim path
    """
    if tool_type == "database":
        path = os.path.join(path, "resc-db-storage")
    if tool_type == "rabbitmq":
        path = os.path.join(path, "resc-rabbitmq-storage")
    if create_dir:
        if not os.path.exists(path):
            os.makedirs(path)
            logging.info(f"Storage created for {tool_type} at {path}")
        else:
            logging.info(
                f"Path already exists. Going to use {path} for {tool_type} storage"
            )

    if operating_system == "windows":
        pvc_path = path.replace(path.split(":")[0], path.split(":")[0].lower())
        pvc_path = pvc_path.replace("\\", "/")
        pvc_path = pvc_path.replace(":", "")
        pvc_path = f"/run/desktop/mnt/host/{pvc_path}"
    else:
        pvc_path = path
    return pvc_path


def prepare_vcs_instances_for_helm_values(helm_values: HelmValue) -> List[VcsInstance]:
    """
        Prepares vcs instances list for helm
    :param helm_values:
        object of HelmValue
    :return: List[VcsInstance]
        Returns list of VCS instances
    """
    vcs_instances: List[VcsInstance] = []
    for vcs in helm_values.vcs_instances:
        if vcs.provider_type == "GITHUB_PUBLIC":
            user_name = "GITHUB_PUBLIC_USERNAME"
            token = "GITHUB_PUBLIC_TOKEN"
        if vcs.provider_type == "AZURE_DEVOPS":
            user_name = "AZURE_DEVOPS_USERNAME"
            token = "AZURE_DEVOPS_TOKEN"
        if vcs.provider_type == "BITBUCKET":
            user_name = "BITBUCKET_USERNAME"
            token = "BITBUCKET_TOKEN"
        vcs_instance_obj = {
            "name": vcs.provider_type,
            "scope": vcs.scope,
            "exceptions": [],
            "providerType": vcs.provider_type,
            "hostname": vcs.host,
            "port": vcs.port,
            "scheme": vcs.scheme,
            "username": user_name,
            "usernameValue": vcs.username,
            "organization": vcs.organization,
            "token": token,
            "tokenValue": vcs.password,
        }
        vcs_instances.append(vcs_instance_obj)
    return vcs_instances


def create_helm_values_yaml(
    helm_values: HelmValue, input_values_yaml_file: str
) -> bool:
    """
        Generates values yaml file for helm deployment of resc
    :param helm_values:
        object of HelmValue
    :param input_values_yaml_file:
        input values.yaml_file path
    :return: bool
        Returns True if file created else returns false
    :raises FileNotFoundError: if example-values.yaml file was not found
    :raises KeyError: if any expected key was not found in the values dictionary
    """
    output_file_generated = False
    output_values_yaml_file = constants.VALUES_FILE
    helm_deployment_help_link = (
        "https://github.com/abnamro/repository-scanner/"
        "blob/main/deployment/kubernetes/README.md"
    )

    try:
        values_dict = read_yaml_file(input_values_yaml_file)

        values_dict["resc-database"]["hostOS"] = helm_values.operating_system
        values_dict["resc-database"]["database"]["pvc_path"] = (
            helm_values.db_storage_path
        )

        values_dict["resc-rabbitmq"]["filemountType"] = helm_values.operating_system
        values_dict["resc-rabbitmq"]["rabbitMQ"]["pvc_path"] = (
            helm_values.rabbitmq_storage_path
        )

        values_dict["resc-database"]["database"]["config"]["password"] = (
            helm_values.db_password
        )
        values_dict["resc-database-init"]["resc"]["config"]["dbPass"] = (
            helm_values.db_password
        )
        values_dict["resc-web-service"]["resc"]["config"]["dbPass"] = (
            helm_values.db_password
        )
        values_dict["resc-web-service-no-auth"]["resc"]["config"]["dbPass"] = (
            helm_values.db_password
        )

        values_dict["resc-vcs-instances"]["vcsInstances"] = (
            prepare_vcs_instances_for_helm_values(helm_values=helm_values)
        )

        with open(output_values_yaml_file, "w", encoding="utf-8") as file_out:
            yaml.dump(values_dict, file_out)
        output_values_yaml_file_path = os.path.abspath(output_values_yaml_file)
        if os.path.exists(output_values_yaml_file_path):
            logging.info(
                f"Helm values yaml file has been successfully generated at {output_values_yaml_file_path}"
            )
            logging.info(
                f"You can proceed with deployment or you can refer to this link "
                f"to make any customizations in helm values yaml file: {helm_deployment_help_link}"
            )
            output_file_generated = True

    except FileNotFoundError:
        logging.error(
            f"Aborting the program! {input_values_yaml_file} file was not found"
        )
        sys.exit(1)
    except KeyError as error:
        logging.error(
            f"Aborting the program! {error} was missing in {input_values_yaml_file}"
        )
        sys.exit(1)
    return output_file_generated


def read_yaml_file(file_path):
    """
        Read content of yaml file
    :param file_path:
        path of yaml file
    :return: stream
        Returns yaml content
    """
    with pkg_resources.resource_stream(__name__, file_path) as file_in:
        data = yaml.safe_load(file_in)
    return data


def get_scheme_host_port_from_url(url: str):
    """
        Get scheme, host, port from url
    :param url:
        url of VCS instance
    :return: str, str, str
        Returns scheme, host, port
    """
    output = urlparse(url)
    if output.port:
        port = str(output.port)
    else:
        port = "443"
    return output.scheme, output.hostname, port


def get_vcs_instance_question_answers() -> List[VcsInstance]:
    """
        Get VCS instance related question answers
    :return: List[VcsInstance]
        Returns list of VCS instances
    """
    vcs_instance_answers = questions.ask_user_to_select_vcs_instance()

    if not vcs_instance_answers:
        logging.error("Aborting the program! No VCS instance was selected")
        sys.exit(1)

    vcs_instances: List[VcsInstance] = []

    for vcs in vcs_instance_answers:
        vcs_instance_info = questions.ask_vcs_instance_details(vcs_type=vcs)
        scheme, host, port = get_scheme_host_port_from_url(vcs_instance_info["url"])
        if vcs == "GitHub":
            default_github_accounts = (
                f"{vcs_instance_info['username']}, kubernetes, docker"
            )
            github_accounts = questions.ask_which_github_accounts_to_scan(
                default_github_accounts=default_github_accounts
            )
            github_account_list = [
                account.strip() for account in github_accounts.split(",")
            ]
            vcs_instance = VcsInstance(
                provider_type="GITHUB_PUBLIC",
                scheme=scheme,
                host=host,
                port=port,
                username=vcs_instance_info["username"],
                password=vcs_instance_info["token"],
                organization=vcs_instance_info["organization"],
                scope=github_account_list,
            )
        if vcs == "Azure Devops":
            vcs_instance = VcsInstance(
                provider_type="AZURE_DEVOPS",
                scheme=scheme,
                host=host,
                port=port,
                username=vcs_instance_info["username"],
                password=vcs_instance_info["token"],
                organization=vcs_instance_info["organization"],
                scope=[],
            )
        if vcs == "Bitbucket":
            vcs_instance = VcsInstance(
                provider_type="BITBUCKET",
                scheme=scheme,
                host=host,
                port=port,
                username=vcs_instance_info["username"],
                password=vcs_instance_info["token"],
                organization=vcs_instance_info["organization"],
                scope=[],
            )
        vcs_instances.append(vcs_instance)
    return vcs_instances


def download_rule_toml_file(url: str, file: str) -> bool:
    """
        Download rule toml file
    :param url:
        url of the file to download
    :param file:
        path of the downloaded file
    :return: bool
        Returns true if rule downloaded successfully else returns false
    """
    downloaded = False
    verify_ssl = questions.ask_ssl_verification(
        msg="Do you want to verify SSL certificates for HTTPS requests?"
    )
    response = requests.get(url, timeout=100, verify=verify_ssl)
    with open(file, "wb") as output:
        output.write(response.content)
    if os.path.exists(file) and os.path.getsize(file) > 0:
        downloaded = True
        logging.debug(f"{file} successfully downloaded")
    else:
        logging.error("Unable to download the rule file")
    return downloaded


def run_deployment_as_per_user_confirmation():
    """
    Run deployment as per user confirmation
    """
    run_deployment_confirm_msg = "Do you want to run deployment?"
    run_deployment_confirm = questions.ask_user_confirmation(
        msg=run_deployment_confirm_msg
    )
    if run_deployment_confirm is True:
        run_deployment()
    else:
        logging.info("Skipping deployment...")


def run_deployment():
    """
        Runs a helm deployment
    :return: bool
        Returns true if deployment successful else returns false
    """
    deployment_status = False

    rule_file_downloaded = download_rule_toml_file(
        url=constants.RULE_FILE_URL, file=constants.RULE_FILE
    )

    add_helm_repository()
    update_helm_repository()

    if rule_file_downloaded:
        namespace_created = create_namespace_if_not_exists(
            namespace_name=constants.NAMESPACE
        )

    if namespace_created:
        # Check if release already exists
        helm_release_exists = check_helm_release_exists()
        if helm_release_exists:
            run_upgrade_confirm_msg = (
                f"Release {constants.RELEASE_NAME} is already installed in "
                f"{constants.NAMESPACE} namespace. Do you want to upgrade the release?"
            )
            run_upgrade_confirm = questions.ask_user_confirmation(
                msg=run_upgrade_confirm_msg
            )
            if run_upgrade_confirm is True:
                deployment_status = install_or_upgrade_helm_release(action="upgrade")
                validate_helm_deployment_status()
            else:
                logging.info("Skipping deployment...")

        else:
            deployment_status = install_or_upgrade_helm_release(action="install")
            validate_helm_deployment_status()
    return deployment_status
