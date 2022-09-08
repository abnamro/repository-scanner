# Standard Library
import unittest

# Third Party
from fastapi.testclient import TestClient

# First Party
from repository_scanner_backend.constants import RWS_ROUTE_HEALTH, RWS_VERSION_PREFIX
from repository_scanner_backend.resc_web_service.api import app
from repository_scanner_backend.resc_web_service.dependencies import requires_auth, requires_no_auth


class TestHealth(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        app.dependency_overrides[requires_auth] = requires_no_auth

    def test_health_check(self):
        response = self.client.get(f"{RWS_VERSION_PREFIX}{RWS_ROUTE_HEALTH}")
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["status"] == "OK"
