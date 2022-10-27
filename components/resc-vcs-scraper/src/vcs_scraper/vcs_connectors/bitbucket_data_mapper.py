
# First Party
from vcs_scraper.dict_remapper import remap_dict_keys

BITBUCKET_BRANCH_MAP = [
    [["id"], ["branch_id"]],
    [["displayId"], ["branch_name"]],
    [["latestCommit"], ["last_scanned_commit"]],
]

BITBUCKET_REPOSITORY_MAP = [
    [["name"], ["repository_name"]],
    [["project", "key"], ["project_key"]],
    [["id"], ["repository_id"]],
]


def map_bitbucket_repository(raw_repository):
    return remap_dict_keys(raw_repository, BITBUCKET_REPOSITORY_MAP)


def map_bitbucket_branch(raw_branch):
    return remap_dict_keys(raw_branch, BITBUCKET_BRANCH_MAP)
