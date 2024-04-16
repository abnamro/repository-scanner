# Standard Library
import logging
import sys

# First Party
from resc_helm_wizard import common, questions
from resc_helm_wizard.helm_value import HelmValue


def prompt_questions():
    """
        prompt set of questions to user in order to generate values yaml file for helm deployment of RESC
    :raises KeyboardInterrupt: if there is any keyboard interruption from user
    """
    try:
        os_input = questions.ask_operating_system()
        if os_input:
            operating_system = common.get_operating_system(user_input=os_input)

        if operating_system:
            storage_path = common.create_storage_for_db_and_rabbitmq(
                operating_system=operating_system
            )
            db_storage_path = storage_path["db_storage_path"]
            rabbitmq_storage_path = storage_path["rabbitmq_storage_path"]

            db_password = questions.ask_password_for_database()

            vcs_instances = common.get_vcs_instance_question_answers()

            if (
                db_password
                and db_storage_path
                and rabbitmq_storage_path
                and vcs_instances
            ):
                helm_values = HelmValue(
                    operating_system=operating_system,
                    db_password=db_password,
                    db_storage_path=db_storage_path,
                    rabbitmq_storage_path=rabbitmq_storage_path,
                    vcs_instances=vcs_instances,
                )

                common.create_helm_values_yaml(
                    helm_values=helm_values,
                    input_values_yaml_file="config/example-values.yaml",
                )
                common.run_deployment_as_per_user_confirmation()
    except KeyboardInterrupt:
        logging.error("Aborting the program! operation cancelled by user")
        sys.exit(-1)


if __name__ == "__main__":
    prompt_questions()
