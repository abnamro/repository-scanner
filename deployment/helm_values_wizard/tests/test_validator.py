# Standard Library
import sys

sys.path.insert(0, "src")
from validator import github_token_validator, password_validator  # noqa: E402  # isort:skip


def test_password_validator():
    validate_1 = password_validator("Lizard")
    validate_2 = password_validator("LizardPass")
    validate_3 = password_validator("LIZARDPASS123")
    validate_4 = password_validator("lizardpass123")
    validate_5 = password_validator("LizardPass123")
    assert validate_1 == "Password must be at least 8 characters"
    assert validate_2 == "Password must contain a number"
    assert validate_3 == "Password must contain a lower-case letter"
    assert validate_4 == "Password must contain an upper-case letter"
    assert validate_5 is True


def test_github_token_validator():
    validate = github_token_validator(token="invalid")
    assert validate == "Validation failed for provided github token"
    validate = github_token_validator(token="ghp_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    assert validate is True
