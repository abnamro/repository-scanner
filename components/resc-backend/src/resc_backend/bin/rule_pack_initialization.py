# pylint: disable=wrong-import-position
# Standard Library
import logging
import os
import shutil

os.environ["GIT_PYTHON_REFRESH"] = "quiet"

# Third Party
import requests
from git.exc import GitCommandNotFound, GitError
from requests.adapters import HTTPAdapter
from urllib3 import Retry

# First Party
from resc_backend.constants import RWS_ROUTE_HEALTH, RWS_ROUTE_RULE_PACKS, RWS_VERSION_PREFIX
from resc_backend.helpers.git_operation import clone_repository
from resc_backend.resc_web_service_interface.rules import upload_rule_pack_toml_file

logger = logging.getLogger()


def wait_for_api_to_up(api_base_url: str):
    """
        This function returns true once the STS API is up.
    :param api_base_url:
        API base url
    :return: True/False
        Returns True if API server is up else returns False
    """

    session = requests.Session()
    retries = Retry(total=100,
                    backoff_factor=1,
                    status_forcelist=[404, 500, 502, 503, 504])
    uri = f"{api_base_url}{RWS_VERSION_PREFIX}{RWS_ROUTE_HEALTH}"
    session.mount("http://", HTTPAdapter(max_retries=retries))
    response = session.get(uri)

    if hasattr(response, "status_code") and int(response.status_code) == 200:
        logger.debug("API server is up")
        return True
    logger.error(f"API is down, HTTP status: '{response.status_code}'")
    return False


def load_toml_rule_into_db(api_base_url: str):
    """
        This function inserts rules in to database.
    :param api_base_url:
        API base url
    :return: Response
        Return response status code after uploading the rules in to database
    """
    try:
        response = None
        api_server_up = wait_for_api_to_up(api_base_url=api_base_url)
        if not api_server_up:
            raise Exception("Wait for API server to up has been failed.")

        tmp_directory = "/tmp"
        repository_url = os.getenv("RULE_PACK_REPOSITORY_URL")
        username = os.getenv("VCS_USERNAME")
        personal_access_token = os.getenv("VCS_ACCESS_TOKEN")
        rule_pack_version_tag = os.getenv("RULE_PACK_VERSION_TAG")
        repository_name = repository_url.split("/")[-1]
        repo_clone_path = f"{tmp_directory}/{repository_name}@{rule_pack_version_tag}"
        toml_file_path = f"{repo_clone_path}/resc_config/RESC-SECRETS-RULE.toml"
        api_url = f"{api_base_url}{RWS_VERSION_PREFIX}{RWS_ROUTE_RULE_PACKS}"

        clone_repository(repository_url=repository_url,
                         branch_name=rule_pack_version_tag,
                         repo_clone_path=repo_clone_path,
                         username=username,
                         personal_access_token=personal_access_token)

        response = upload_rule_pack_toml_file(url=api_url, rule_file_path=toml_file_path)
    except GitCommandNotFound as error:
        logger.error(f"git executable is not found in path. error: {error}")
    except GitError as error:
        logger.error(f"Error occurred while cloning the repository "
                     f"repository: {repository_url}::tag:{rule_pack_version_tag}"
                     f" error: {error}")
    finally:
        # Make sure the repo cloned path removed
        logger.debug(f"Cleaning up the temporary rule repository: {repo_clone_path}")
        if repo_clone_path and os.path.exists(repo_clone_path):
            shutil.rmtree(repo_clone_path)
            logger.debug("Cleaned up the repository directory successfully")
    return response
