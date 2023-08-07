# Standard Library
from unittest.mock import ANY, MagicMock, patch

# Third Party
import pytest
from fastapi import Request, Response

# First Party
from resc_backend.constants import CACHE_PREFIX
from resc_backend.resc_web_service.cache_manager import CacheManager


@pytest.fixture(autouse=True)
def env_setup(monkeypatch):
    monkeypatch.setenv("RESC_REDIS_CACHE_ENABLE", "true")
    monkeypatch.setenv("RESC_REDIS_SERVICE_HOST", "localhost")
    monkeypatch.setenv("RESC_REDIS_SERVICE_PORT", "6379")
    monkeypatch.setenv("REDIS_PASSWORD", "dummy_password")


@patch("fastapi_cache.FastAPICache.init")
@patch("resc_backend.resc_web_service.cache_manager.CacheManager.get_cache_client")
@patch("resc_backend.resc_web_service.cache_manager.CacheManager.request_key_builder")
def test_initialize_cache_with_cache_enabled(mock_request_key_builder, mock_get_cache_client, mock_cache_init):
    mock_request_key_builder.return_value = "test-key"
    mock_get_cache_client.return_value = None
    mock_cache_init.return_value = None
    env_variables = {"RESC_REDIS_CACHE_ENABLE": "true",
                     "RESC_REDIS_SERVICE_HOST": "localhost",
                     "RESC_REDIS_SERVICE_PORT": "6379",
                     "REDIS_PASSWORD": "dummy_password"}
    CacheManager.initialize_cache(env_variables)
    mock_get_cache_client.assert_called_once_with(host="localhost", port=int("6379"), password="dummy_password")
    mock_cache_init.assert_called_once_with(ANY, prefix=CACHE_PREFIX,
                                            key_builder=mock_request_key_builder,
                                            enable=True)


@patch("fastapi_cache.FastAPICache.init")
def test_initialize_cache_with_cache_disabled(mock_cache_init):
    mock_cache_init.return_value = None
    env_variables = {"RESC_REDIS_CACHE_ENABLE": "false"}
    CacheManager.initialize_cache(env_variables)
    mock_cache_init.assert_called_once_with(backend=ANY, enable=False)


@patch("fastapi_cache.FastAPICache.get_prefix")
@patch("logging.Logger.debug")
def test_request_key_builder(mock_debug_log, mock_get_prefix):
    mock_get_prefix.return_value = CACHE_PREFIX
    mock_request = MagicMock(spec=Request)
    mock_request.method = "GET"
    mock_request.url.path = "http://example.com/path"
    mock_request.query_params.items.return_value = ["param", "value"]
    expected_cache_key = f"{CACHE_PREFIX}:test-namespace:get:http://example.com/path:['param', 'value']"
    expected_debug_msg = f"Cache created with key: {expected_cache_key}"
    response = Response()
    cache_key = CacheManager.request_key_builder(
        func=None, namespace="test-namespace", request=mock_request, response=response, args=None, kwargs=None,
    )
    assert cache_key == expected_cache_key
    mock_debug_log.assert_called_once_with(expected_debug_msg)


@patch("fastapi_cache.FastAPICache.get_prefix")
@patch("logging.Logger.debug")
def test_personalized_key_builder(mock_debug_log, mock_get_prefix):
    mock_get_prefix.return_value = CACHE_PREFIX
    mock_request = MagicMock(spec=Request)
    mock_request.method = "GET"
    mock_request.url.path = "http://example.com/path"
    mock_request.user = "test-user"
    mock_request.query_params.items.return_value = ["param", "value"]
    expected_cache_key = f"{CACHE_PREFIX}:test-namespace:test-user:get:http://example.com/path:['param', 'value']"
    expected_debug_msg = f"Cache created with key: {expected_cache_key}"
    response = Response()
    cache_key = CacheManager.personalized_key_builder(
        func=None, namespace="test-namespace", request=mock_request, response=response, args=None, kwargs=None,
    )
    assert cache_key == expected_cache_key
    mock_debug_log.assert_called_once_with(expected_debug_msg)


@pytest.mark.asyncio
@patch("fastapi_cache.FastAPICache.get_enable")
@patch("fastapi_cache.FastAPICache.clear")
@patch("logging.Logger.debug")
async def test_clear_cache_by_namespace(mock_debug_log, mock_clear, mock_get_enable):
    mock_clear.return_value = None
    mock_get_enable.return_value = True
    namespace = "test-namespace"
    expected_debug_msg = f"Cache cleared for namespaces: {namespace}"
    await CacheManager.clear_cache_by_namespace(namespace=namespace)
    mock_clear.assert_called_once_with(namespace=namespace)
    mock_debug_log.assert_called_once_with(expected_debug_msg)


@pytest.mark.asyncio
@patch("fastapi_cache.FastAPICache.get_enable")
@patch("fastapi_cache.FastAPICache.clear")
@patch("logging.Logger.debug")
async def test_clear_all_cache(mock_debug_log, mock_clear, mock_get_enable):
    mock_clear.return_value = None
    mock_get_enable.return_value = True
    expected_debug_msg = "Cache cleared for all namespaces"
    await CacheManager.clear_all_cache()
    mock_clear.assert_called_once()
    mock_debug_log.assert_called_once_with(expected_debug_msg)
