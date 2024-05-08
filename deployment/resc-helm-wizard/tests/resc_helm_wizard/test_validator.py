# Standard Library

# First Party
from resc_helm_wizard.validator import (
    azure_devops_token_validator,
    bitbucket_token_validator,
    github_account_name_validator,
    github_token_validator,
    github_username_validator,
    password_validator,
    vcs_url_validator,
)


def test_password_validator():
    error_message = (
        "Password must contain at least one upper case, one lower case, "
        "one number, one special character and the length of the password to be between 8 and 128"
    )
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
    validate = azure_devops_token_validator(
        token="123456dummytoken123456789012345dummytoken12345123456"
    )
    assert validate is True


def test_bitbucket_token_validator():
    validate = bitbucket_token_validator(token="invalid")
    assert validate == "Validation failed for provided Bitbucket token"
    validate = bitbucket_token_validator(
        token="123456dummyToken123456789012345+dummytoken12"
    )
    assert validate is True


def test_github_account_name_validator():
    validate = github_account_name_validator(github_accounts="Lizard!, Liza")
    assert (
        validate == "Lizard! is not a valid GitHub account. GitHub account "
        "must contain alphanumeric characters or single hyphens, "
        "can't begin or end with a hyphen and maximum 39 characters allowed."
    )
    validate = github_account_name_validator(github_accounts="")
    assert (
        validate
        == "Please enter a valid comma separated list of GitHub accounts you want to scan"
    )
    validate = github_account_name_validator(github_accounts="Lizard")
    assert validate is True


def test_github_username_validator():
    validate = github_username_validator(username="Lizard!")
    assert (
        validate == "Lizard! is not a valid GitHub username. GitHub username "
        "must contain alphanumeric characters or single hyphens, "
        "can't begin or end with a hyphen and maximum 39 characters allowed."
    )
    validate = github_username_validator(username="Lizard")
    assert validate is True


def test_vcs_url_validator():
    validate = vcs_url_validator(url="https://github.com")
    assert validate is True
    validate = vcs_url_validator(url="http://github.com")
    assert validate is True
    validate = vcs_url_validator(url="http://github.com:443")
    assert validate is True
    validate = vcs_url_validator(url="http://github.com:-443")
    assert validate == "Please provide a valid URL"
    validate = vcs_url_validator(url="http:github")
    assert validate == "Please provide a valid URL"
    validate = vcs_url_validator(url="ftp://github")
    assert validate == "Please provide a valid URL"
