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
    regex = re.compile(
        r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{8,128}$"
    )

    if not re.fullmatch(regex, password):
        return (
            "Password must contain at least one upper case, one lower case, one number, "
            "one special character and the length of the password to be between 8 and 128"
        )
    return True


def github_token_validator(token: str):
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

    if not re.fullmatch(classic_pat_regex, token) and not re.fullmatch(
        fine_grained_pat_regex, token
    ):
        return "Validation failed for provided GitHub token"
    return True


def azure_devops_token_validator(token: str):
    """
        Personal access token validator for Azure Devops
    :param token:
        token which needs to be validated
    :return: str or bool.
        If validation fails, the output will contain a validation error message.
        Otherwise, the output will return true if validation was successful
    """
    regex = re.compile(r"^[a-z0-9]{52}$")

    if not re.fullmatch(regex, token):
        return "Validation failed for provided Azure DevOps token"
    return True


def bitbucket_token_validator(token):
    """
        Personal access token validator for Bitbucket
    :param token:
        token which needs to be validated
    :return: str or bool.
        If validation fails, the output will contain a validation error message.
        Otherwise, the output will return true if validation was successful
    """
    regex = re.compile(r"^(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z]).{40,50}$")

    if not re.fullmatch(regex, token):
        return "Validation failed for provided Bitbucket token"
    return True


def github_account_name_validator(github_accounts):
    """
        GitHub account name validator
    :param github_accounts:
        comma separated list of GitHub accounts
    :return: str or bool.
        If validation fails, the output will contain a validation error message.
        Otherwise, the output will return true if validation was successful
    """
    input_list = [elem.strip() for elem in github_accounts.split(",")]
    regex = re.compile(r"^[a-zA-Z\d](?:[a-zA-Z\d]|-(?=[a-zA-Z\d])){0,38}$")
    for account in input_list:
        if not re.fullmatch(regex, account):
            if account:
                msg = (
                    f"{account} is not a valid GitHub account. "
                    f"GitHub account must contain alphanumeric characters or single hyphens, "
                    f"can't begin or end with a hyphen and maximum 39 characters allowed."
                )
            else:
                msg = "Please enter a valid comma separated list of GitHub accounts you want to scan"
            return msg
    return True


def github_username_validator(username):
    """
        GitHub username validator
    :param username:
        username of GitHub account
    :return: str or bool.
        If validation fails, the output will contain a validation error message.
        Otherwise, the output will return true if validation was successful
    """
    regex = re.compile(r"^[a-zA-Z\d](?:[a-zA-Z\d]|-(?=[a-zA-Z\d])){0,38}$")

    if not re.fullmatch(regex, username):
        msg = (
            f"{username} is not a valid GitHub username. "
            f"GitHub username must contain alphanumeric characters or single hyphens, "
            f"can't begin or end with a hyphen and maximum 39 characters allowed."
        )
        return msg
    return True


def vcs_url_validator(url):
    """
        VCS provider url validator
    :param url:
        url which needs to be validated
    :return: str or bool.
        If validation fails, the output will contain a validation error message.
        Otherwise, the output will return true if validation was successful
    """
    regex = re.compile(
        r"^(?:http)s?://"  # Scheme
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # Domain
        r"localhost|"  # Localhost
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # IP address
        r"(?::\d+)?"  # Port (optional)
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )  # Path and query (optional)

    if not re.fullmatch(regex, url):
        return "Please provide a valid URL"
    return True
