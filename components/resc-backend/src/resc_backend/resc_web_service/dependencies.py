# Standard Library
import logging
import ssl
import urllib.error

# Third Party
import jwt
import sqlalchemy.orm
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBasicCredentials, HTTPBearer
from jwt import PyJWKClient
from tenacity import retry, stop_after_attempt, wait_exponential

# First Party
from resc_backend.constants import (
    CACHE_CONTROL,
    CONTENT_SECURITY_POLICY,
    CROSS_ORIGIN_RESOURCE_POLICY,
    REFERRER_POLICY,
    STRICT_TRANSPORT_SECURITY,
    X_CONTENT_TYPE_OPTIONS,
    X_FRAME_OPTIONS,
    X_PERMITTED_CROSS_DOMAIN_POLICIES,
    X_XSS_PROTECTION
)
from resc_backend.db.connection import Session, engine
from resc_backend.db.model import DBfinding, DBrepository, DBrule, DBscan, DBscanFinding
from resc_backend.helpers.environment_wrapper import validate_environment
from resc_backend.resc_web_service.configuration import (
    CONDITIONAL_SSO_ENV_VARS,
    SSO_ACCESS_TOKEN_ISSUER_URL,
    SSO_ACCESS_TOKEN_JWKS_URL,
    SSO_JWT_CLAIM_KEY_AUTHORIZATION,
    SSO_JWT_CLAIM_KEY_USER_ID,
    SSO_JWT_CLAIM_VALUE_AUTHORIZATION,
    SSO_JWT_REQUIRED_CLAIMS,
    SSO_JWT_SIGN_ALGORITHM
)

security = HTTPBearer()
logger = logging.getLogger(__name__)


async def requires_auth(request: Request, credentials: HTTPBasicCredentials = Depends(security)):
    """
        Function that is used to validate the JWT access token
    """
    # Check and load environment variables
    env_variables = validate_environment(CONDITIONAL_SSO_ENV_VARS)

    access_token = credentials.credentials
    algorithm = [env_variables[SSO_JWT_SIGN_ALGORITHM]]
    issuer = env_variables[SSO_ACCESS_TOKEN_ISSUER_URL]
    jwks_url = env_variables[SSO_ACCESS_TOKEN_JWKS_URL]
    jwt_options = {
        "verify_signature": True, "verify_iss": True, "verify_exp": True,
        "require": env_variables[SSO_JWT_REQUIRED_CLAIMS].split(",")
    }
    try:
        ssl._create_default_https_context = ssl._create_unverified_context  # pylint: disable=W0212
        jwks_client = PyJWKClient(jwks_url)
        signing_key = jwks_client.get_signing_key_from_jwt(access_token)
        claims = jwt.decode(
            access_token,
            signing_key.key,
            algorithms=algorithm,
            issuer=issuer,
            options=jwt_options,
        )
        user_id = claims[env_variables[SSO_JWT_CLAIM_KEY_USER_ID]]
        if not user_is_authorized(claims, env_variables):
            logger.error(f"Invalid login attempt for user {user_id}")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="You don't have permission to access this resource.")
        request.scope["user"] = user_id
    except urllib.error.URLError as error:
        logger.error(f"Unable to contact server for token validation {jwks_url} Message: {error}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Unable to contact server for token validation") from error

    except jwt.InvalidAlgorithmError as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Algorithm is invalid for decoding token",
                            headers={"WWW-Authenticate": "Bearer"}) from error
    except jwt.PyJWKClientError as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unable to find the signing key",
                            headers={"WWW-Authenticate": "Bearer"}) from error
    except jwt.InvalidKeyError as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="JWKS key is not in the proper format",
                            headers={"WWW-Authenticate": "Bearer"}) from error
    except jwt.InvalidIssuerError as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Token's issuer claim does not match with the expected issuer",
                            headers={"WWW-Authenticate": "Bearer"}) from error
    except jwt.ExpiredSignatureError as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired",
                            headers={"WWW-Authenticate": "Bearer"}) from error
    except jwt.InvalidSignatureError as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token's signature did not match",
                            headers={"WWW-Authenticate": "Bearer"}) from error
    except jwt.DecodeError as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Token can not be decoded because it failed validation",
                            headers={"WWW-Authenticate": "Bearer"}) from error
    except jwt.InvalidTokenError as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token",
                            headers={"WWW-Authenticate": "Bearer"}) from error


async def add_security_headers(request: Request, call_next):
    """
        Function that is used to add several security headers to the API
    """
    security_headers = {
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
    response = await call_next(request)
    for header, value in security_headers.items():
        response.headers[header] = value
    return response


def user_is_authorized(claims: dict, env_variables: dict) -> bool:
    """
        Function that is used to determine if the user has the required claim and value to access the web service
    """
    claim_key = env_variables[SSO_JWT_CLAIM_KEY_AUTHORIZATION]
    claim_check_value = env_variables[SSO_JWT_CLAIM_VALUE_AUTHORIZATION]
    return bool(claim_key in claims and claim_check_value in claims[claim_key])


def requires_no_auth(request: Request):
    """
        Function that is used for unauthenticated access
    """
    request.scope["user"] = "Anonymous"


def get_db_connection():
    db_connection = Session(bind=engine)
    try:
        yield db_connection
    finally:
        db_connection.close()


@retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(100))
def check_db_initialized():
    required_table_names = [
        DBfinding.__tablename__,
        DBrepository.__tablename__,
        DBrule.__tablename__,
        DBscan.__tablename__,
        DBscanFinding.__tablename__
    ]
    try:
        # Create a sqlalchemy inspector, will cause an exception if the db connection can't be established
        inspector = sqlalchemy.inspect(engine)

        # Check existence of required tables
        not_found_tables = []
        for table_name in required_table_names:
            table_exists = inspector.has_table(table_name)
            if not table_exists:
                not_found_tables.append(table_name)

        if len(not_found_tables) > 0:
            raise RuntimeError(f"Unable to determine existence of required table(s) "
                               f"{', '.join(not_found_tables)}")
    except Exception as ex:
        logger.error(f"Database is NOT connected or initialized | {ex} | Retrying...")
        raise
