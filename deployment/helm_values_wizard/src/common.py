# Standard Library
import logging
import os
import sys

# Third Party
import questionary
import yaml

# First Party
from helm_values import HelmValues

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


def create_storage_for_db_and_rabbitmq(operating_system: str):
    """
        Creates volume storage for database and rabbitmq
    :param operating_system:
        operating system
    :return: str, str
        Returns database storage and rabbitmq storage path
    """
    default_local_storage = os.path.expanduser('~')

    local_storage = questionary.path(message="Where would you like to create the local storage for RESC. default is ",
                                     default=default_local_storage, only_directories=True).unsafe_ask()

    if os.path.exists(local_storage):
        db_storage_path = generate_pvc_path(operating_system=operating_system, path=local_storage, tool_type="database",
                                            create_dir=True)
        rabbitmq_storage_path = generate_pvc_path(operating_system=operating_system, path=local_storage,
                                                  tool_type="rabbitmq", create_dir=True)
    else:
        dir_confirm = questionary.confirm(f"Do you want to create the directory {local_storage}?").unsafe_ask()
        if dir_confirm is True:
            db_storage_path = generate_pvc_path(operating_system=operating_system, path=local_storage,
                                                tool_type="database", create_dir=True)
            rabbitmq_storage_path = generate_pvc_path(operating_system=operating_system, path=local_storage,
                                                      tool_type="rabbitmq", create_dir=True)
        else:
            logging.warning(
                "Warning! Please ensure the provided directory exists on the system where you are running the "
                "deployment.")
            proceed_confirm = questionary.confirm("Are you sure you want to proceed?").unsafe_ask()
            if proceed_confirm is False:
                logging.info("Aborting the program!!")
                sys.exit()
            else:
                db_storage_path = generate_pvc_path(operating_system=operating_system, path=local_storage,
                                                    tool_type="database", create_dir=False)
                rabbitmq_storage_path = generate_pvc_path(operating_system=operating_system, path=local_storage,
                                                          tool_type="rabbitmq", create_dir=False)
    return db_storage_path, rabbitmq_storage_path


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


def create_helm_values_yaml(helm_values: HelmValues):
    """
        Generates values yaml file for helm deployment of resc
    :param helm_values:
        object of HelmValues
    :raises FileNotFoundError: if example-values.yaml file was not found
    :raises KeyError: if any expected key was not found in the values dictionary
    """
    input_values_yaml_file = "../kubernetes/example-values.yaml"
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

        for vcs_instance in values_dict["resc-vcs-instances"]["vcsInstances"]:
            if vcs_instance["providerType"] == "GITHUB_PUBLIC":
                vcs_instance["usernameValue"] = helm_values.github_username
                vcs_instance["tokenValue"] = helm_values.github_token

        with open(output_values_yaml_file, "w", encoding="utf-8") as file_out:
            yaml.dump(values_dict, file_out)
        output_values_yaml_file_path = os.path.abspath(output_values_yaml_file)
        if os.path.exists(output_values_yaml_file_path):
            logging.info(f"Helm values yaml file has been successfully generated at {output_values_yaml_file_path}")
            logging.info(
                f"Please refer this link to continue with the deployment "
                f"or to make any customizations: {helm_deployment_help_link}")
        else:
            logging.error("Aborting the program! Error while generating helm values yaml file")
            sys.exit()

    except FileNotFoundError:
        logging.error("Aborting the program! example-values.yaml file was not found")
        sys.exit()
    except KeyError as error:
        logging.error(f"Aborting the program! {error} was missing in {input_values_yaml_file}")
        sys.exit()
