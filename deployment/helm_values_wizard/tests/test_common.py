# Standard Library
import sys

# First Party
from common import get_operating_system

sys.path.insert(0, "src")


def test_get_operating_system_windows():
    operating_system = get_operating_system(user_input="Microsoft Windows")
    assert operating_system == "windows"


def test_get_operating_system_linux():
    operating_system = get_operating_system(user_input="Linuxws")
    assert operating_system == "linux"
