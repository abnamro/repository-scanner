
# First Party
from vcs_scraper.dict_remapper import remap_dict_keys

AZURE_DEVOPS_BRANCH_INFO_MAP = [
    [["name"], ["branch_id"]],
    [["name"], ["branch_name"]],
    [["commit", "commit_id"], ["last_scanned_commit"]],
]

AZURE_DEVOPS_REPOSITORY_INFO_MAP = [
    [["name"], ["repository_name"]],
    [["project", "name"], ["project_key"]],
    [["id"], ["repository_id"]],
    [["web_url"], ["repository_url"]],
]


def map_azure_devops_repository_info(raw_repository_info):
    return remap_dict_keys(raw_repository_info, AZURE_DEVOPS_REPOSITORY_INFO_MAP)


def map_azure_devops_branch_info(raw_branch_info):
    return remap_dict_keys(raw_branch_info, AZURE_DEVOPS_BRANCH_INFO_MAP)
