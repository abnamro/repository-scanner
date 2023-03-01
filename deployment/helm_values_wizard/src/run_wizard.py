# Standard Library
import logging
import sys

# Third Party
import questionary

# First Party
from common import (
    create_helm_values_yaml,
    create_storage_for_db_and_rabbitmq,
    get_operating_system
)
from helm_values import HelmValues
from validator import github_token_validator, password_validator


def prompt_questions():
    """
        prompt set of questions to user in order to generate values yaml file for helm deployment of RESC
    :raises KeyboardInterrupt: if there is any keyboard interruption from user
    """
    try:
        os_input = questionary.select(
            message="Which operating system are you running on the target environment",
            choices=["Microsoft Windows", "macOS", "Linux"]).unsafe_ask()
        if os_input:
            operating_system = get_operating_system(user_input=os_input)

        if operating_system:
            db_storage_path, rabbitmq_storage_path = create_storage_for_db_and_rabbitmq(
                operating_system=operating_system)

            db_password = questionary.password("Please enter the password you want to set for database",
                                               validate=password_validator).unsafe_ask()

            github_username = questionary.text("What's your github username").unsafe_ask()
            github_token = questionary.password("Please enter your github personal access token",
                                                validate=github_token_validator).unsafe_ask()

            if (db_password and db_storage_path and
                    rabbitmq_storage_path and github_username and github_token):
                helm_values = HelmValues(
                    operating_system=operating_system,
                    db_password=db_password,
                    db_storage_path=db_storage_path,
                    rabbitmq_storage_path=rabbitmq_storage_path,
                    github_username=github_username,
                    github_token=github_token
                )

                create_helm_values_yaml(helm_values)
    except KeyboardInterrupt:
        logging.error("Aborting the program! operation cancelled by user")
        sys.exit()


if __name__ == '__main__':
    prompt_questions()
