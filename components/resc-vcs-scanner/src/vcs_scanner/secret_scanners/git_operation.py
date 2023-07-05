# pylint: disable=bad-option-value,C0413
# Standard Library
import logging
import os

os.environ["GIT_PYTHON_REFRESH"] = "quiet"

# Third Party
from git import Repo  # noqa: E402

logger = logging.getLogger(__name__)


def clone_repository(repository_url: str,
                     repo_clone_path: str,
                     username: str = "",
                     personal_access_token: str = "") -> None:
    """
        Clones the given repository
    :param repository_url:
        Repository url to clone
    :param repo_clone_path:
        Path where to clone the repository
    :param username:
        Username to clone the repository, only needed if the repository is private
    :param personal_access_token:
        Personal access token|password to clone the repository, only needed if the repository is private
    """
    url = repository_url.replace("https://", "")
    repo_clone_url = f"https://{username}:{personal_access_token}@{url}"
    Repo.clone_from(repo_clone_url, repo_clone_path)
    logger.debug(f"Repository {repository_url} cloned successfully")
