# Standard Library
import sys
from unittest.mock import patch

# First Party
from run_wizard import prompt_questions

sys.path.insert(0, "src")


@patch("questions.ask_operating_system")
@patch("common.create_storage_for_db_and_rabbitmq")
@patch("questions.ask_password_for_database")
@patch("common.get_vcs_instance_question_answers")
@patch("common.create_helm_values_yaml")
def test_prompt_questions(create_helm_values_yaml, get_vcs_instance_question_answers,
                          ask_password_for_database, create_storage_for_db_and_rabbitmq,
                          ask_operating_system):
    ask_operating_system.return_value = "Linux"
    storage_path = {"db_storage_path": "/tmp/resc-db-storage", "rabbitmq_storage_path": "/tmp/resc-rabbitmq-storage"}
    create_storage_for_db_and_rabbitmq.return_value = storage_path
    ask_password_for_database.return_value = "test"
    get_vcs_instance_question_answers.return_value = []
    create_helm_values_yaml.return_value = True

    prompt_questions()
    get_vcs_instance_question_answers.assert_called_once_with()
    ask_password_for_database.assert_called_once_with()
    create_storage_for_db_and_rabbitmq.assert_called_once_with(operating_system="linux")
    ask_operating_system.assert_called_once_with()
