# Standard Library
import logging
from typing import Any, Callable, Dict, Tuple

# Third Party
from fastapi import Request, Response
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

# First Party
from resc_backend.common import initialise_logs
from resc_backend.constants import CACHE_PREFIX, LOG_FILE_CACHING
from resc_backend.helpers.environment_wrapper import validate_environment
from resc_backend.resc_web_service.configuration import (
    CONDITIONAL_REDIS_ENV_VARS,
    REDIS_PASSWORD,
    RESC_REDIS_CACHE_ENABLE,
    RESC_REDIS_SERVICE_HOST,
    RESC_REDIS_SERVICE_PORT
)

logger_config = initialise_logs(LOG_FILE_CACHING)
logger = logging.getLogger(__name__)


class CacheManager:

    @classmethod
    def initialize_cache(cls, env_variables):
        cache_enabled = env_variables[RESC_REDIS_CACHE_ENABLE].lower() in ["true"]
        if cache_enabled:
            env_variables.update(validate_environment(CONDITIONAL_REDIS_ENV_VARS))
            redis_host = f"{env_variables[RESC_REDIS_SERVICE_HOST]}"
            redis_port = f"{env_variables[RESC_REDIS_SERVICE_PORT]}"
            redis_password = f"{env_variables[REDIS_PASSWORD]}"
            redis_backend = cls.get_cache_client(host=redis_host, port=int(redis_port), password=redis_password)
            FastAPICache.init(RedisBackend(redis_backend),
                              prefix=CACHE_PREFIX,
                              key_builder=cls.request_key_builder,
                              enable=cache_enabled)
        else:
            FastAPICache.init(backend=RedisBackend(None), enable=cache_enabled)

    @staticmethod
    def get_cache_client(host: str, port: int, password: str):
        cache_client = aioredis.from_url(f"redis://{host}:{port}", password=password)
        return cache_client

    @staticmethod
    def request_key_builder(func: Callable[..., Any],  # pylint: disable=W0613
                            namespace: str = "",
                            *,
                            request: Request = None,
                            response: Response = None,  # pylint: disable=W0613
                            args: Tuple[Any, ...], kwargs: Dict[str, Any]) -> str:  # pylint: disable=W0613
        """
        Build a unique key for caching based on the provided function, namespace, request, response,
        arguments (args), and keyword arguments (kwargs).

        Args:
            func (Callable): The function for which the key is being built.
            namespace (str, optional): A namespace to differentiate keys (default "").
            request (Request, optional): The request object (default None).
            response (Response, optional): The response object (default None).
            args (Tuple[Any, ...]): Positional arguments passed to the function.
            kwargs (Dict[str, Any]): Keyword arguments passed to the function.

        Returns:
            str: A unique key based on the input parameters.
        """

        cache_key = ":".join([
            FastAPICache.get_prefix(),
            namespace,
            request.method.lower(),
            request.url.path,
            repr(sorted(request.query_params.items()))
        ])
        logger.debug(f"Cache created with key: {cache_key}")
        return cache_key

    @staticmethod
    def personalized_key_builder(func: Callable[..., Any],  # pylint: disable=W0613
                                 namespace: str = "",
                                 *,
                                 request: Request = None,
                                 response: Response = None,  # pylint: disable=W0613
                                 args: Tuple[Any, ...], kwargs: Dict[str, Any]) -> str:  # pylint: disable=W0613
        """
        Build a personalized unique key for caching based logged-in user on the provided function, namespace, request,
        response, arguments (args), and keyword arguments (kwargs).
        This should be used for apis specific to logged-in user.

        Args:
            func (Callable): The function for which the key is being built.
            namespace (str, optional): A namespace to differentiate keys (default "").
            request (Request, optional): The request object (default None).
            response (Response, optional): The response object (default None).
            args (Tuple[Any, ...]): Positional arguments passed to the function.
            kwargs (Dict[str, Any]): Keyword arguments passed to the function.

        Returns:
            str: A unique key based on the input parameters.
        """
        cache_key = ":".join([
            CACHE_PREFIX,
            namespace,
            request.user,
            request.method.lower(),
            request.url.path,
            repr(sorted(request.query_params.items()))
        ])
        logger.debug(f"Cache created with key: {cache_key}")
        return cache_key

    @staticmethod
    async def clear_cache_by_namespace(namespace):
        cache_enabled = FastAPICache.get_enable()
        if cache_enabled:
            await FastAPICache.clear(namespace=namespace)
            logger.debug(f"Cache cleared for namespaces: {namespace}")

    @staticmethod
    async def clear_all_cache():
        cache_enabled = FastAPICache.get_enable()
        if cache_enabled:
            await FastAPICache.clear()
            logger.debug("Cache cleared for all namespaces")
