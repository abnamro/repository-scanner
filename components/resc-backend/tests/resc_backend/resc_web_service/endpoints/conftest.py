# Standard Library
import os

# Third Party
import mock

mock.patch("fastapi_cache.decorator.cache", lambda *args, **kwargs: lambda f: f).start()
os.environ.setdefault('RESC_REDIS_CACHE_ENABLE', 'False')
