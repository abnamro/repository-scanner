# Standard Library
from unittest.mock import patch

# First Party
from repository_scanner_backend.helpers.git_operation import clone_repository


@patch("git.repo.base.Repo.clone_from")
def test_clone_repository(clone_from):
    username = "username"
    personal_access_token = "personal_access_token"
    repository_url = "https://fake-host.com"
    branch_name = "branch_name"
    repo_clone_path = "repo_clone_path"

    clone_repository(repository_url=repository_url,
                     branch_name=branch_name, repo_clone_path=repo_clone_path, username=username,
                     personal_access_token=personal_access_token)

    clone_from.assert_called_once()
    url = repository_url.replace("https://", "")
    expected_repo_clone_url = f"https://{username}:{personal_access_token}@{url}"
    clone_from.assert_called_once_with(expected_repo_clone_url, repo_clone_path, branch=branch_name)
