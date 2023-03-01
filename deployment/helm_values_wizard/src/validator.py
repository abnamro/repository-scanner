# Standard Library
import re


def password_validator(password: str):
    """
        Password validator for database
    :param password:
        password which needs to be validated
    :return: str or bool.
        If validation fails, the output will contain a validation error message.
        Otherwise, the output will return true if validation was successful
    """
    if len(password) < 9:
        return "Password must be at least 8 characters"
    if re.search("[0-9]", password) is None:
        return "Password must contain a number"
    if re.search("[a-z]", password) is None:
        return "Password must contain a lower-case letter"
    if re.search("[A-Z]", password) is None:
        return "Password must contain an upper-case letter"
    return True


def github_token_validator(token):
    """
        Personal access token validator for GitHub
    :param token:
        token which needs to be validated
    :return: str or bool.
        If validation fails, the output will contain a validation error message.
        Otherwise, the output will return true if validation was successful
    """
    classic_pat_regex = re.compile(r"^ghp_[a-zA-Z0-9]{36}$")
    fine_grained_pat_regex = re.compile(r"^github_pat_[a-zA-Z0-9]{22}_[a-zA-Z0-9]{59}$")

    if not re.fullmatch(classic_pat_regex, token) and not re.fullmatch(fine_grained_pat_regex, token):
        return "Validation failed for provided github token"
    return True
