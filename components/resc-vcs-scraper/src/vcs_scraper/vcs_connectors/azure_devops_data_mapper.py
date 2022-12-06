
# First Party
from vcs_scraper.dict_remapper import remap_dict_keys

AZURE_DEVOPS_BRANCH_MAP = [
    [["name"], ["branch_id"]],
    [["name"], ["branch_name"]],
    [["commit", "commit_id"], ["latest_commit"]],
]

AZURE_DEVOPS_REPOSITORY_MAP = [
    [["name"], ["repository_name"]],
    [["project", "name"], ["project_key"]],
    [["id"], ["repository_id"]],
    [["web_url"], ["repository_url"]],
]


def map_azure_devops_repository(raw_repository):
    return remap_dict_keys(raw_repository, AZURE_DEVOPS_REPOSITORY_MAP)


def map_azure_devops_branch(raw_branch):
    return remap_dict_keys(raw_branch, AZURE_DEVOPS_BRANCH_MAP)
