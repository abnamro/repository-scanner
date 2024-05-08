# Standard Library
from unittest.mock import patch

# First Party
from resc_helm_wizard.run_wizard import prompt_questions


@patch("resc_helm_wizard.questions.ask_operating_system")
@patch("resc_helm_wizard.common.create_storage_for_db_and_rabbitmq")
@patch("resc_helm_wizard.questions.ask_password_for_database")
@patch("resc_helm_wizard.common.get_vcs_instance_question_answers")
@patch("resc_helm_wizard.common.create_helm_values_yaml")
@patch("resc_helm_wizard.common.run_deployment_as_per_user_confirmation")
def test_prompt_questions(
    run_deployment_as_per_user_confirmation,
    create_helm_values_yaml,
    get_vcs_instance_question_answers,
    ask_password_for_database,
    create_storage_for_db_and_rabbitmq,
    ask_operating_system,
):
    ask_operating_system.return_value = "Linux"
    storage_path = {
        "db_storage_path": "/tmp/resc-db-storage",
        "rabbitmq_storage_path": "/tmp/resc-rabbitmq-storage",
    }
    create_storage_for_db_and_rabbitmq.return_value = storage_path
    ask_password_for_database.return_value = "test"
    get_vcs_instance_question_answers.return_value = []
    create_helm_values_yaml.return_value = True
    run_deployment_as_per_user_confirmation.return_value = True

    prompt_questions()
    get_vcs_instance_question_answers.assert_called_once_with()
    ask_password_for_database.assert_called_once_with()
    create_storage_for_db_and_rabbitmq.assert_called_once_with(operating_system="linux")
    ask_operating_system.assert_called_once_with()
