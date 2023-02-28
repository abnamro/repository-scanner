# Standard Library
import sys

# Third Party
# import pytest

# First Party
sys.path.insert(0, "src")
from common import get_operating_system  # noqa: E402  # isort:skip


def test_get_operating_system_windows():
    operating_system = get_operating_system(operating_system_input="Microsoft Windows")
    assert operating_system == "windows"


def test_get_operating_system_linux():
    operating_system = get_operating_system(operating_system_input="Linuxws")
    assert operating_system == "linux"
