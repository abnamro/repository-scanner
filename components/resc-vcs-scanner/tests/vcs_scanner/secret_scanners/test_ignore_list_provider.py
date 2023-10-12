# Standard Library
from pathlib import Path

# First Party
from vcs_scanner.secret_scanners.ignore_list_provider import IgnoredListProvider


THIS_DIR = Path(__file__).parent.parent

# We check that given a file, we get only 1 line:
def test_ignore_list_provider():
    ignore_list_path = THIS_DIR.parent / "fixtures/ignore-findings-list.dsv"
    listProvider = IgnoredListProvider(str(ignore_list_path))
    assert {'active_path|active_rule|57': True, 'active_path_2|active_rule_2|58': True} == listProvider.get_ignore_list()
