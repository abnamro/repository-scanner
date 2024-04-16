# Standard Library
import os

# Third Party
import questionary

# First Party
from resc_helm_wizard import constants
from resc_helm_wizard.validator import (
    azure_devops_token_validator,
    bitbucket_token_validator,
    github_account_name_validator,
    github_token_validator,
    github_username_validator,
    password_validator,
    vcs_url_validator,
)


def ask_operating_system() -> str:
    """
        Asks user to select operating system
    :return: str
        Returns user selected operating system
    """
    answer = questionary.select(
        message="Which operating system are you running on the target environment",
        choices=["Microsoft Windows", "macOS", "Linux"],
    ).unsafe_ask()
    return answer


def ask_local_storage_path() -> str:
    """
        Asks user to provide path for local storage
    :return: str
        Returns user provided local storage path
    """
    default_local_storage = os.path.expanduser("~")
    answer = questionary.path(
        message="Where would you like to create the local storage for RESC. default is ",
        default=default_local_storage,
        only_directories=True,
    ).unsafe_ask()
    return answer


def ask_password_for_database() -> str:
    """
        Asks user to provide password for database
    :return: str
        Returns user provided password for database
    """
    answer = questionary.password(
        "Please enter the password you want to set for database",
        validate=password_validator,
    ).unsafe_ask()
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
        "Select VCS instance for which you want to run the scan",
        choices=[
            "GitHub",
            "Azure Devops",
            "Bitbucket",
        ],
        default="GitHub",
    ).unsafe_ask()
    return answer


def ask_vcs_instance_details(vcs_type: str) -> dict:
    """
        Asks user to provide vcs instances details
    :return: dict
        Returns vcs instance info
    """
    username = "NA"
    organization = ""

    if vcs_type == "GitHub":
        url = questionary.text(
            f"Please enter {vcs_type} url",
            default=constants.DEFAULT_GITHUB_URL,
            validate=vcs_url_validator,
        ).unsafe_ask()
        username = questionary.text(
            f"What's your {vcs_type} username", validate=github_username_validator
        ).unsafe_ask()
        token = questionary.password(
            f"Please enter your {vcs_type} personal access token",
            validate=github_token_validator,
        ).unsafe_ask()

    if vcs_type == "Bitbucket":
        url = questionary.text(
            f"Please enter {vcs_type} url", validate=vcs_url_validator
        ).unsafe_ask()
        username = questionary.text(f"What's your {vcs_type} username").unsafe_ask()
        token = questionary.password(
            f"Please enter your {vcs_type} personal access token",
            validate=bitbucket_token_validator,
        ).unsafe_ask()

    if vcs_type == "Azure Devops":
        url = questionary.text(
            f"Please enter {vcs_type} url",
            default=constants.DEFAULT_AZURE_DEVOPS_URL,
            validate=vcs_url_validator,
        ).unsafe_ask()
        organization = questionary.text(
            f"What's your organization name in {vcs_type}"
        ).unsafe_ask()
        token = questionary.password(
            f"Please enter your {vcs_type} personal access token",
            validate=azure_devops_token_validator,
        ).unsafe_ask()
    vcs_instance_info = {
        "url": url,
        "organization": organization,
        "username": username,
        "token": token,
    }
    return vcs_instance_info


def ask_which_github_accounts_to_scan(default_github_accounts: str) -> [str]:
    """
        Asks user to provide GitHub account names to scan
    :return: [str]
        Returns array of GitHub account names
    """
    github_accounts = questionary.text(
        "Enter a comma separated list of GitHub accounts you want to scan",
        default=default_github_accounts,
        validate=github_account_name_validator,
    ).unsafe_ask()
    return github_accounts


def ask_ssl_verification(msg: str) -> bool:
    """
        Asks for ssl verification
    :param msg:
        confirmation message
    :return: bool
        Returns True or False based on user's confirmation
    """
    answer = questionary.confirm(msg, default=True).unsafe_ask()
    return answer
