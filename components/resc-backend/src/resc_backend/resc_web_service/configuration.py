# coding=utf-8
# First Party
from resc_backend.helpers.environment_wrapper import EnvironmentVariable

ENABLE_CORS = 'ENABLE_CORS'
CORS_ALLOWED_DOMAINS = 'CORS_ALLOWED_DOMAINS'

AUTHENTICATION_REQUIRED = 'AUTHENTICATION_REQUIRED'
SSO_ACCESS_TOKEN_ISSUER_URL = 'SSO_ACCESS_TOKEN_ISSUER_URL'
SSO_ACCESS_TOKEN_JWKS_URL = 'SSO_ACCESS_TOKEN_JWKS_URL'
SSO_JWT_SIGN_ALGORITHM = 'SSO_JWT_SIGN_ALGORITHM'
SSO_JWT_REQUIRED_CLAIMS = 'SSO_JWT_REQUIRED_CLAIMS'
SSO_JWT_CLAIM_KEY_USER_ID = 'SSO_JWT_CLAIM_KEY_USER_ID'
SSO_JWT_CLAIM_KEY_AUTHORIZATION = 'SSO_JWT_CLAIM_KEY_AUTHORIZATION'
SSO_JWT_CLAIM_VALUE_AUTHORIZATION = 'SSO_JWT_CLAIM_VALUE_AUTHORIZATION'

RESC_REDIS_CACHE_ENABLE = 'RESC_REDIS_CACHE_ENABLE'
RESC_REDIS_SERVICE_HOST = 'RESC_REDIS_SERVICE_HOST'
RESC_REDIS_SERVICE_PORT = 'RESC_REDIS_SERVICE_PORT'
REDIS_PASSWORD = 'REDIS_PASSWORD'

WEB_SERVICE_ENV_VARS = [
    EnvironmentVariable(
        ENABLE_CORS,
        "Enable by providing the value true to allow CORS requests.",
        required=False,
        default='',
    ),
    EnvironmentVariable(
        CORS_ALLOWED_DOMAINS,
        "Comma separated lists of domains to allow in the CORS policy if ENABLE_CORS is true",
        required=False,
        default='',
    ),
    EnvironmentVariable(
        AUTHENTICATION_REQUIRED,
        "set to false to disable authentication, any other value will enable SSO authentication",
        required=False,
        default='',
    ),
    EnvironmentVariable(
        RESC_REDIS_CACHE_ENABLE,
        "Set to true to enable the redis cache, its expected to be running separately from this instance",
        required=False,
        default='False',
    )
]

CONDITIONAL_SSO_ENV_VARS = [
    EnvironmentVariable(
        SSO_ACCESS_TOKEN_ISSUER_URL,
        "URL of the access token issuer",
        required=True,
    ),
    EnvironmentVariable(
        SSO_ACCESS_TOKEN_JWKS_URL,
        "URL of the access token JWKS",
        required=True,
    ),
    EnvironmentVariable(
        SSO_JWT_SIGN_ALGORITHM,
        "signing algorithm used for the JWT, for example RS256",
        required=True,
    ),
    EnvironmentVariable(
        SSO_JWT_REQUIRED_CLAIMS,
        "Comma separated list of claims that need to be in the JWT",
        required=True,
    ),
    EnvironmentVariable(
        SSO_JWT_CLAIM_KEY_USER_ID,
        "JWT claim key used for the user id",
        required=True,
    ),
    EnvironmentVariable(
        SSO_JWT_CLAIM_KEY_AUTHORIZATION,
        "JWT claim key used for the authorization check",
        required=True,
    ),
    EnvironmentVariable(
        SSO_JWT_CLAIM_VALUE_AUTHORIZATION,
        "JWT claim value used for the authorization check. "
        "Used as string contains check on the key from SSO_JWT_CLAIM_KEY_AUTHORIZATION",
        required=True,
    ),
]

CONDITIONAL_REDIS_ENV_VARS = [
    EnvironmentVariable(
        RESC_REDIS_SERVICE_HOST,
        "The hostname/IP address of the REDIS server.",
        required=True,
    ),
    EnvironmentVariable(
        RESC_REDIS_SERVICE_PORT,
        "The port on which the REDIS server is running.",
        required=True,
    ),
    EnvironmentVariable(
        REDIS_PASSWORD,
        "The REDIS authentication secret.",
        required=True,
    ),
]
