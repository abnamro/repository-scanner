# Standard Library
import logging
import os
import sys
from typing import List
from urllib.parse import urlparse

# Third Party
import yaml

# First Party
import questions
from helm_value import HelmValue
from vcs_instance import VcsInstance

logging.basicConfig(level=logging.DEBUG)


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
        db_storage_path = generate_pvc_path(operating_system=operating_system, path=local_storage, tool_type="database",
                                            create_dir=True)
        rabbitmq_storage_path = generate_pvc_path(operating_system=operating_system, path=local_storage,
                                                  tool_type="rabbitmq", create_dir=True)
    else:
        dir_confirm_msg = f"Do you want to create the directory {local_storage}?"
        dir_confirm = questions.ask_user_confirmation(msg=dir_confirm_msg)
        if dir_confirm is True:
            db_storage_path = generate_pvc_path(operating_system=operating_system, path=local_storage,
                                                tool_type="database", create_dir=True)
            rabbitmq_storage_path = generate_pvc_path(operating_system=operating_system, path=local_storage,
                                                      tool_type="rabbitmq", create_dir=True)
        else:
            logging.warning(
                "Warning! Please ensure the provided directory exists on the system where you are running the "
                "deployment")
            proceed_confirm = questions.ask_user_confirmation(msg="Are you sure you want to proceed?")
            if proceed_confirm is True:
                db_storage_path = generate_pvc_path(operating_system=operating_system, path=local_storage,
                                                    tool_type="database", create_dir=False)
                rabbitmq_storage_path = generate_pvc_path(operating_system=operating_system, path=local_storage,
                                                          tool_type="rabbitmq", create_dir=False)
            else:
                logging.info("Aborting the program!!")
                sys.exit()
    storage_path = {"db_storage_path": db_storage_path, "rabbitmq_storage_path": rabbitmq_storage_path}
    return storage_path


def generate_pvc_path(operating_system: str, path: str, tool_type: str, create_dir: bool) -> str:
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
            logging.info(f"Path already exists. Going to use {path} for {tool_type} storage")

    if operating_system == "windows":
        pvc_path = path.replace(path.split(':')[0], path.split(':')[0].lower())
        pvc_path = pvc_path.replace('\\', '/')
        pvc_path = pvc_path.replace(':', '')
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
        vcs_instance_obj = {"name": vcs.provider_type, "scope": vcs.scope, "exceptions": [],
                            "providerType": vcs.provider_type, "hostname": vcs.host, "port": vcs.port,
                            "scheme": vcs.scheme, "username": user_name, "usernameValue": vcs.username,
                            "organization": vcs.organization, "token": token, "tokenValue": vcs.password}
        vcs_instances.append(vcs_instance_obj)
    return vcs_instances


def create_helm_values_yaml(helm_values: HelmValue, input_values_yaml_file: str):
    """
        Generates values yaml file for helm deployment of resc
    :param helm_values:
        object of HelmValue
    :param input_values_yaml_file:
        input values.yaml_file path
    :raises FileNotFoundError: if example-values.yaml file was not found
    :raises KeyError: if any expected key was not found in the values dictionary
    """
    output_values_yaml_file = "custom-values.yaml"
    helm_deployment_help_link = "https://github.com/abnamro/repository-scanner/" \
                                "blob/main/deployment/kubernetes/README.md"

    try:
        with open(input_values_yaml_file, "r", encoding="utf-8") as file_in:
            values_dict = yaml.safe_load(file_in)

        values_dict["resc-database"]["hostOS"] = helm_values.operating_system
        values_dict["resc-database"]["database"]["pvc_path"] = helm_values.db_storage_path

        values_dict["resc-rabbitmq"]["filemountType"] = helm_values.operating_system
        values_dict["resc-rabbitmq"]["rabbitMQ"]["pvc_path"] = helm_values.rabbitmq_storage_path

        values_dict["resc-database"]["database"]["config"]["password"] = helm_values.db_password
        values_dict["resc-database-init"]["resc"]["config"]["dbPass"] = helm_values.db_password
        values_dict["resc-web-service"]["resc"]["config"]["dbPass"] = helm_values.db_password
        values_dict["resc-web-service-no-auth"]["resc"]["config"]["dbPass"] = helm_values.db_password

        values_dict["resc-vcs-instances"]["vcsInstances"] = prepare_vcs_instances_for_helm_values(
            helm_values=helm_values)

        with open(output_values_yaml_file, "w", encoding="utf-8") as file_out:
            yaml.dump(values_dict, file_out)
        output_values_yaml_file_path = os.path.abspath(output_values_yaml_file)
        if os.path.exists(output_values_yaml_file_path):
            logging.info(
                f"Helm values yaml file has been successfully generated at {output_values_yaml_file_path}. "
                f"Please refer this link to continue with the deployment or "
                f"to make any customizations: {helm_deployment_help_link}")

    except FileNotFoundError:
        logging.error(f"Aborting the program! {input_values_yaml_file} file was not found")
        sys.exit()
    except KeyError as error:
        logging.error(f"Aborting the program! {error} was missing in {input_values_yaml_file}")
        sys.exit()


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
        sys.exit()

    vcs_instances: List[VcsInstance] = []

    for vcs in vcs_instance_answers:
        vcs_instance_info = questions.ask_vcs_instance_details(vcs_type=vcs)
        scheme, host, port = get_scheme_host_port_from_url(vcs_instance_info["url"])
        if vcs == "GitHub":
            vcs_instance = VcsInstance(
                provider_type="GITHUB_PUBLIC",
                scheme=scheme,
                host=host,
                port=port,
                username=vcs_instance_info["username"],
                password=vcs_instance_info["token"],
                organization=vcs_instance_info["organization"],
                scope=["kubernetes", "docker"]
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
                scope=[]
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
                scope=[]
            )
        vcs_instances.append(vcs_instance)
    return vcs_instances
