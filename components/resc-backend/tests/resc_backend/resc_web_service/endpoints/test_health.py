# Standard Library
import unittest

# Third Party
from fastapi.testclient import TestClient

# First Party
from resc_backend.constants import (
    CACHE_CONTROL,
    CONTENT_SECURITY_POLICY,
    CROSS_ORIGIN_RESOURCE_POLICY,
    REFERRER_POLICY,
    RWS_ROUTE_HEALTH,
    RWS_VERSION_PREFIX,
    STRICT_TRANSPORT_SECURITY,
    X_CONTENT_TYPE_OPTIONS,
    X_FRAME_OPTIONS,
    X_PERMITTED_CROSS_DOMAIN_POLICIES,
    X_XSS_PROTECTION
)
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
            "Strict-Transport-Security": STRICT_TRANSPORT_SECURITY,
            "Cache-Control": CACHE_CONTROL,
            "Cross-Origin-Resource-Policy": CROSS_ORIGIN_RESOURCE_POLICY,
            "Referrer-Policy": REFERRER_POLICY,
            "X-Permitted-Cross-Domain-Policies": X_PERMITTED_CROSS_DOMAIN_POLICIES,
            "X-Content-Type-Options": X_CONTENT_TYPE_OPTIONS,
            "X-Frame-Options": X_FRAME_OPTIONS,
            "X-XSS-Protection": X_XSS_PROTECTION,
            "Content-Security-Policy": CONTENT_SECURITY_POLICY
        }
        response = self.client.get(f"{RWS_VERSION_PREFIX}{RWS_ROUTE_HEALTH}")
        assert response.status_code == 200, response.text
        for header, value in correct_security_headers.items():
            assert header in response.headers
            assert value == response.headers[header]
