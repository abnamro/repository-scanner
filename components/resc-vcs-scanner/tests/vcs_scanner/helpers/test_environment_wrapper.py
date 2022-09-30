# Standard Library
import os
import sys
from unittest import TestCase, mock

sys.path.insert(0, "src")
from vcs_scanner.helpers.environment_wrapper import (  # noqa: E402  # isort:skip
    validate_environment,
    EnvironmentVariable
)

REQUIRED_ENV_VARS = [
    EnvironmentVariable(
        "REQUIRED_CONFIG",
        "A Sample required configuration",
        required=True,
    ),
    EnvironmentVariable(
        "NOT_REQUIRED_CONFIG",
        "A Sample not required configuration",
        required=False,
    )
]

REQUIRED_CONFIG = "value"


def test_validate_environment():
    env_variables = validate_environment(REQUIRED_ENV_VARS)
    assert env_variables["REQUIRED_CONFIG"] == REQUIRED_CONFIG
    assert env_variables["NOT_REQUIRED_CONFIG"] == ""


class ErrorTests(TestCase):
    # Make sure to set required env vars to empty first
    @mock.patch.dict(os.environ, {"REQUIRED_CONFIG": ""})
    def test_validate_environment_required(self):
        self.assertRaises(EnvironmentError, validate_environment,
                          REQUIRED_ENV_VARS)
