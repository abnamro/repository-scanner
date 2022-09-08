# Standard Library
from unittest.mock import patch

# Third Party
import pytest
from tenacity import RetryError, stop_after_attempt

# First Party
from repository_scanner_backend.constants import RESC_OPERATOR_ROLE
from repository_scanner_backend.resc_web_service.dependencies import check_db_initialized, user_has_resc_operator_role


# Tests how the method responds to a person with the correct role; RESC_OPERATOR_ROLE
def test_correct_user_role():
    claims = {"roles": RESC_OPERATOR_ROLE}
    assert user_has_resc_operator_role(claims)


# Tests how the method responds to a person with the incorrect role; PCP_OPERATOR_ROLE
def test_incorrect_user_role():
    claims = {"roles": "Invalid role"}
    assert not user_has_resc_operator_role(claims)


# Tests how the method responds to an empty role; " "
def test_empty_user_role():
    claims = {"roles": ""}
    assert not user_has_resc_operator_role(claims)


def test_no_claims():
    claims = {}
    assert not user_has_resc_operator_role(claims)


@patch("logging.Logger.error")
@patch("sqlalchemy.engine.reflection.Inspector.has_table")
def test_check_db_initialized_false(has_table, error_logger):
    check_db_initialized.retry.stop = stop_after_attempt(1)
    has_table.return_value = False

    with pytest.raises(RetryError):
        check_db_initialized()

    error_logger.assert_called_once_with("Database is NOT connected or initialized | Unable to determine existence of "
                                         "required table(s) branch_info, finding, repository_info, rules, scan, "
                                         "scan_finding | Retrying...")


@patch("logging.Logger.error")
@patch("sqlalchemy.engine.reflection.Inspector.has_table")
def test_check_db_initialized_true(has_table, error_logger):
    has_table.return_value = True
    try:
        check_db_initialized()
    except SystemExit:
        pytest.fail("Unexpected SystemExit ..")
    error_logger.assert_not_called()
