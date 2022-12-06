# Standard Library
import unittest

# Third Party
from fastapi.testclient import TestClient

# First Party
from resc_backend.constants import (
    AZURE_DEVOPS,
    BITBUCKET,
    GITHUB_PUBLIC,
    RWS_ROUTE_AUTH_CHECK,
    RWS_ROUTE_SUPPORTED_VCS_PROVIDERS,
    RWS_VERSION_PREFIX
)
from resc_backend.resc_web_service.api import app


class TestFindings(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_get_supported_vcs_providers(self):
        response = self.client.get(f"{RWS_VERSION_PREFIX}"
                                   f"{RWS_ROUTE_SUPPORTED_VCS_PROVIDERS}")
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data) == 3
        assert data[0] == AZURE_DEVOPS
        assert data[1] == BITBUCKET
        assert data[2] == GITHUB_PUBLIC

    def test_auth_check(self):
        response = self.client.get(f"{RWS_VERSION_PREFIX}"
                                   f"{RWS_ROUTE_AUTH_CHECK}")
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data) == 1
        assert data["message"] == "OK"
