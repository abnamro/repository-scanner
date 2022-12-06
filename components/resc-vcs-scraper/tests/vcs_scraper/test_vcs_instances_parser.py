# Standard Library
import os
from pathlib import Path

# Third Party
from mock import mock

# First Party
from vcs_scraper.vcs_instances_parser import parse_vcs_instances_file

read_data = "{}"
mock_open = mock.mock_open(read_data=read_data)

THIS_DIR = Path(__file__).parent


def test_parse_vcs_instances_file():

    my_data_path = THIS_DIR.parent / "fixtures/working_vcs_instances.json"
    with mock.patch.dict(os.environ, {"VCS_INSTANCE_TOKEN": "token123", "VCS_INSTANCE_USERNAME": "user123"}):
        vcs_instances = parse_vcs_instances_file(str(my_data_path))
    assert vcs_instances[0].provider_type == "AZURE_DEVOPS"
    assert vcs_instances[0].port == 443
    assert vcs_instances[0].name == "vcs_instance_1"
    assert vcs_instances[0].exceptions == []
    assert vcs_instances[0].hostname == "dev.azure.com"
    assert vcs_instances[0].scheme == "https"
    assert vcs_instances[0].username == "user123"
    assert vcs_instances[0].token == "token123"
    assert vcs_instances[0].scope == []
    assert vcs_instances[0].organization == "org"

    assert vcs_instances[1].provider_type == "BITBUCKET"
    assert vcs_instances[1].port == 1234
    assert vcs_instances[1].name == "vcs_instance_2"
    assert vcs_instances[1].exceptions == []
    assert vcs_instances[1].hostname == "bitbucket.com"
    assert vcs_instances[1].scheme == "https"
    assert vcs_instances[1].username == "user123"
    assert vcs_instances[1].token == "token123"
    assert vcs_instances[1].scope == []
    assert vcs_instances[1].organization is None


def test_parse_vcs_instances_file_with_missing_org():

    my_data_path = THIS_DIR.parent / "fixtures/missing_org_ado_vcs_instances.json"
    assert [] == parse_vcs_instances_file(str(my_data_path))


def test_parse_vcs_instances_file_with_mal_formatted_file():

    my_data_path = THIS_DIR.parent / "fixtures/non_json.file"
    assert [] == parse_vcs_instances_file(str(my_data_path))


def test_parse_vcs_instances_file_with_missing_file():

    my_data_path = THIS_DIR.parent / "fixtures/non_there.file"
    assert [] == parse_vcs_instances_file(str(my_data_path))
