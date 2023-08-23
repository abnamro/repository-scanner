# Standard Library
import unittest
from typing import Generator
from unittest.mock import ANY

# Third Party
import pytest
from fastapi.testclient import TestClient
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend

# First Party
from resc_backend.constants import (
    AZURE_DEVOPS,
    BITBUCKET,
    CACHE_PREFIX,
    GITHUB_PUBLIC,
    REDIS_CACHE_EXPIRE,
    RWS_ROUTE_AUTH_CHECK,
    RWS_ROUTE_SUPPORTED_VCS_PROVIDERS,
    RWS_VERSION_PREFIX
)
from resc_backend.resc_web_service.api import app
from resc_backend.resc_web_service.cache_manager import CacheManager
from resc_backend.resc_web_service.dependencies import requires_auth, requires_no_auth


@pytest.fixture(autouse=True)
def _init_cache() -> Generator[ANY, ANY, None]:
    FastAPICache.init(InMemoryBackend(),
                      prefix=CACHE_PREFIX,
                      expire=REDIS_CACHE_EXPIRE,
                      key_builder=CacheManager.request_key_builder,
                      enable=True)
    yield
    FastAPICache.reset()


class TestFindings(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        app.dependency_overrides[requires_auth] = requires_no_auth

    @staticmethod
    def assert_cache(cached_response):
        assert FastAPICache.get_enable() is True
        assert FastAPICache.get_prefix() == CACHE_PREFIX
        assert FastAPICache.get_expire() == REDIS_CACHE_EXPIRE
        assert FastAPICache.get_key_builder() is not None
        assert FastAPICache.get_coder() is not None
        assert cached_response.headers.get("cache-control") is not None

    def test_get_supported_vcs_providers(self):
        with self.client as client:
            response = client.get(f"{RWS_VERSION_PREFIX}"
                                  f"{RWS_ROUTE_SUPPORTED_VCS_PROVIDERS}")
            assert response.status_code == 200, response.text
            data = response.json()
            assert len(data) == 3
            assert data[0] == AZURE_DEVOPS
            assert data[1] == BITBUCKET
            assert data[2] == GITHUB_PUBLIC

            # Make the second request to retrieve response from cache
            cached_response = client.get(f"{RWS_VERSION_PREFIX}"
                                         f"{RWS_ROUTE_SUPPORTED_VCS_PROVIDERS}")
            self.assert_cache(cached_response)
            assert response.json() == cached_response.json()

    def test_auth_check(self):
        response = self.client.get(f"{RWS_VERSION_PREFIX}"
                                   f"{RWS_ROUTE_AUTH_CHECK}")
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data) == 1
        assert data["message"] == "OK"
