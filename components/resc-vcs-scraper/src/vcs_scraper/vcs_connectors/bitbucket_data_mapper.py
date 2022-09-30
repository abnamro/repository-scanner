
# First Party
from vcs_scraper.dict_remapper import remap_dict_keys

BITBUCKET_BRANCH_INFO_MAP = [
    [["id"], ["branch_id"]],
    [["displayId"], ["branch_name"]],
    [["latestCommit"], ["last_scanned_commit"]],
]

BITBUCKET_REPOSITORY_INFO_MAP = [
    [["name"], ["repository_name"]],
    [["project", "key"], ["project_key"]],
    [["id"], ["repository_id"]],
]


def map_bitbucket_repository_info(raw_repository_info):
    return remap_dict_keys(raw_repository_info, BITBUCKET_REPOSITORY_INFO_MAP)


def map_bitbucket_branch_info(raw_branch_info):
    return remap_dict_keys(raw_branch_info, BITBUCKET_BRANCH_INFO_MAP)
