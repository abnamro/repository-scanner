# Third Party
import pytest


@pytest.fixture(autouse=True)
def env_setup(monkeypatch):
    monkeypatch.setenv('REQUIRED_CONFIG', 'value')
