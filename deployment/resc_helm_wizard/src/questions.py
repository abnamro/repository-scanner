# Standard Library
import os

# Third Party
import questionary

# First Party
from validator import (
    azure_devops_token_validator,
    bitbucket_token_validator,
    github_token_validator,
    password_validator
)


def ask_operating_system() -> str:
    """
        Asks user to select operating system
    :return: str
        Returns user selected operating system
    """
    answer = questionary.select(
        message="Which operating system are you running on the target environment",
        choices=["Microsoft Windows", "macOS", "Linux"]).unsafe_ask()
    return answer


def ask_local_storage_path() -> str:
    """
        Asks user to provide path for local storage
    :return: str
        Returns user provided local storage path
    """
    default_local_storage = os.path.expanduser('~')
    answer = questionary.path(message="Where would you like to create the local storage for RESC. default is ",
                              default=default_local_storage, only_directories=True).unsafe_ask()
    return answer


def ask_password_for_database() -> str:
    """
        Asks user to provide password for database
    :return: str
        Returns user provided password for database
    """
    answer = questionary.password("Please enter the password you want to set for database",
                                  validate=password_validator).unsafe_ask()
    return answer


def ask_user_confirmation(msg: str) -> bool:
    """
        Asks user to provide confirmation
    :param msg:
        confirmation message
    :return: bool
        Returns True or False based on user's confirmation
    """
    answer = questionary.confirm(msg).unsafe_ask()
    return answer


def ask_user_to_select_vcs_instance() -> [str]:
    """
        Asks user to select vcs instances
    :return: [str]
        Returns array of user selected vcs instances
    """
    answer = questionary.checkbox(
        'Select VCS instance for which you want to run the scan',
        choices=[
            "GitHub",
            "Azure Devops",
            "Bitbucket",
        ],
        default="GitHub").unsafe_ask()
    return answer


def ask_vcs_instance_details(vcs_type: str) -> dict:
    """
        Asks user to provide vcs instances details
    :return: dict
        Returns vcs instance info
    """
    username = "NA"
    organization = ""
    url = questionary.text(f"Please enter {vcs_type} url").unsafe_ask()

    if vcs_type == "GitHub":
        username = questionary.text(f"What's your {vcs_type} username").unsafe_ask()
        token = questionary.password(f"Please enter your {vcs_type} personal access token",
                                     validate=github_token_validator).unsafe_ask()

    if vcs_type == "Bitbucket":
        username = questionary.text(f"What's your {vcs_type} username").unsafe_ask()
        token = questionary.password(f"Please enter your {vcs_type} personal access token",
                                     validate=bitbucket_token_validator).unsafe_ask()

    if vcs_type == "Azure Devops":
        organization = questionary.text(f"What's your organization name in {vcs_type}").unsafe_ask()
        token = questionary.password(f"Please enter your {vcs_type} personal access token",
                                     validate=azure_devops_token_validator).unsafe_ask()
    vcs_instance_info = {"url": url, "organization": organization, "username": username, "token": token}
    return vcs_instance_info
