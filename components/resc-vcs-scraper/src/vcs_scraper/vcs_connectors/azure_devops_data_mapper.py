
# First Party
from vcs_scraper.dict_remapper import remap_dict_keys

AZURE_DEVOPS_REPOSITORY_MAP = [
    [["name"], ["repository_name"]],
    [["project", "name"], ["project_key"]],
    [["id"], ["repository_id"]],
    [["web_url"], ["repository_url"]],
]


def map_azure_devops_repository(raw_repository):
    return remap_dict_keys(raw_repository, AZURE_DEVOPS_REPOSITORY_MAP)
