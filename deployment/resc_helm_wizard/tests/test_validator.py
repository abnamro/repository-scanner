# Standard Library
import sys

# First Party
from validator import (
    azure_devops_token_validator,
    bitbucket_token_validator,
    github_token_validator,
    password_validator
)

sys.path.insert(0, "src")


def test_password_validator():
    error_message = "Password must contain at least one upper case, one lower case, " \
                    "one number, one special character and the length of the password to be between 8 and 128"
    validate_1 = password_validator("Lizard")
    validate_2 = password_validator("LizardPass")
    validate_3 = password_validator("LIZARDPASS123")
    validate_4 = password_validator("lizardpass123")
    validate_5 = password_validator("LizardPass@123")
    assert validate_1 == error_message
    assert validate_2 == error_message
    assert validate_3 == error_message
    assert validate_4 == error_message
    assert validate_5 is True


def test_github_token_validator():
    validate = github_token_validator(token="invalid")
    assert validate == "Validation failed for provided GitHub token"
    validate = github_token_validator(token="ghp_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    assert validate is True


def test_azure_devops_token_validator():
    validate = azure_devops_token_validator(token="invalid")
    assert validate == "Validation failed for provided Azure DevOps token"
    validate = azure_devops_token_validator(token="123456dummytoken123456789012345dummytoken12345123456")
    assert validate is True


def test_bitbucket_token_validator():
    validate = bitbucket_token_validator(token="invalid")
    assert validate == "Validation failed for provided Bitbucket token"
    validate = bitbucket_token_validator(token="123456dummyToken123456789012345+dummytoken12")
    assert validate is True
