# Standard Library
import unittest

# Third Party
from fastapi.testclient import TestClient

# First Party
from resc_backend.constants import RWS_ROUTE_HEALTH, RWS_VERSION_PREFIX
from resc_backend.resc_web_service.api import app
from resc_backend.resc_web_service.dependencies import requires_auth, requires_no_auth


class TestHealth(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        app.dependency_overrides[requires_auth] = requires_no_auth

    def test_health_check(self):
        response = self.client.get(f"{RWS_VERSION_PREFIX}{RWS_ROUTE_HEALTH}")
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["status"] == "OK"

    def test_correct_security_headers(self):
        correct_security_headers = {
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
            "Cache-Control": "no-cache, no-store",
            "Cross-Origin-Resource-Policy": "same-site",
            "Referrer-Policy": "same-origin",
            "X-Permitted-Cross-Domain-Policies": "none",
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Content-Security-Policy": "default-src 'none'; script-src 'self'; "
                                       "connect-src 'self'; img-src 'self' data:;"
                                       " style-src 'self' https://fonts.googleapis.com 'unsafe-inline';"
                                       " frame-ancestors 'self'; form-action 'self';"
        }
        response = self.client.get(f"{RWS_VERSION_PREFIX}{RWS_ROUTE_HEALTH}")
        assert response.status_code == 200, response.text
        for header, value in correct_security_headers.items():
            assert header in response.headers
            assert value == response.headers[header]
