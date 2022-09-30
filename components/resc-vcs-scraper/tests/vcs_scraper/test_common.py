# Standard Library
import os
from pathlib import Path
from typing import Dict

# Third Party
from mock import mock
from mock.mock import patch

# First Party
from vcs_scraper.common import load_vcs_instances_into_map
from vcs_scraper.model import VCSInstance

THIS_DIR = Path(__file__).parent


def test_load_vcs_instances_into_map():
    my_data_path = THIS_DIR.parent / "fixtures/working_vcs_instances.json"
    with mock.patch.dict(os.environ, {"VCS_INSTANCE_TOKEN": "token123", "VCS_INSTANCE_USERNAME": "user123"}):
        vcs_instances_map: Dict[str, VCSInstance] = load_vcs_instances_into_map(str(my_data_path))
    element1 = list(vcs_instances_map.keys())[0]
    element2 = list(vcs_instances_map.keys())[1]

    assert vcs_instances_map[element1].provider_type == "AZURE_DEVOPS"
    assert vcs_instances_map[element1].port == 443
    assert vcs_instances_map[element1].name == "vcs_instance_1"
    assert vcs_instances_map[element1].exceptions == []
    assert vcs_instances_map[element1].hostname == "dev.azure.com"
    assert vcs_instances_map[element1].scheme == "https"
    assert vcs_instances_map[element1].username == "user123"
    assert vcs_instances_map[element1].token == "token123"
    assert vcs_instances_map[element1].scope == []
    assert vcs_instances_map[element1].organization == "org"

    assert vcs_instances_map[element2].provider_type == "BITBUCKET"
    assert vcs_instances_map[element2].port == 1234
    assert vcs_instances_map[element2].name == "vcs_instance_2"
    assert vcs_instances_map[element2].exceptions == []
    assert vcs_instances_map[element2].hostname == "bitbucket.com"
    assert vcs_instances_map[element2].scheme == "https"
    assert vcs_instances_map[element2].username == "user123"
    assert vcs_instances_map[element2].token == "token123"
    assert vcs_instances_map[element2].scope == []
    assert vcs_instances_map[element2].organization is None


@patch("sys.exit")
def test_load_vcs_instances_into_map_with_missing_org(sys_exit):

    my_data_path = THIS_DIR.parent / "fixtures/missing_org_ado_vcs_instances.json"
    assert {} == load_vcs_instances_into_map(str(my_data_path))
    assert sys_exit.called
