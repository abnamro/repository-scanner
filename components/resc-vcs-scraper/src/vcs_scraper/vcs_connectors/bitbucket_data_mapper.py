
# First Party
from vcs_scraper.dict_remapper import remap_dict_keys

BITBUCKET_REPOSITORY_MAP = [
    [["name"], ["repository_name"]],
    [["project", "key"], ["project_key"]],
    [["id"], ["repository_id"]],
]


def map_bitbucket_repository(raw_repository):
    return remap_dict_keys(raw_repository, BITBUCKET_REPOSITORY_MAP)
