# Standard Library
from typing import List

# Third Party
from fastapi import APIRouter, status
from fastapi_cache.decorator import cache

# First Party
from resc_backend.constants import (
    CACHE_NAMESPACE_VCS_INSTANCE,
    COMMON_TAG,
    ERROR_MESSAGE_500,
    ERROR_MESSAGE_503,
    REDIS_CACHE_EXPIRE,
    RWS_ROUTE_AUTH_CHECK,
    RWS_ROUTE_SUPPORTED_VCS_PROVIDERS
)
from resc_backend.resc_web_service.schema.vcs_provider import VCSProviders

router = APIRouter(tags=[COMMON_TAG])


@router.get(f"{RWS_ROUTE_SUPPORTED_VCS_PROVIDERS}",
            response_model=List[str],
            summary="Get supported vcs-providers",
            description="Retrieve the supported vcs-providers, example: Bitbucket, AzureDevOps, Github etc",
            status_code=status.HTTP_200_OK,
            responses={
                200: {"description": "Retrieve the supported vcs-providers"},
                500: {"description": ERROR_MESSAGE_500},
                503: {"description": ERROR_MESSAGE_503}
            })
@cache(namespace=CACHE_NAMESPACE_VCS_INSTANCE, expire=REDIS_CACHE_EXPIRE)
def get_supported_vcs_providers() -> List[str]:
    """
        Retrieve all supported vcs providers
    :return: List[str]
        The output will contain a list of strings of unique vcs providers
    """
    supported_vcs = [vcs for vcs in VCSProviders if vcs]
    return supported_vcs


@router.get(f"{RWS_ROUTE_AUTH_CHECK}",
            summary="Authorization check",
            description="The output returns 200 OK if auth check is successful else returns 403 Forbidden",
            status_code=status.HTTP_200_OK,
            responses={
                200: {"description": "Validate authorization check from the access-token"},
                500: {"description": ERROR_MESSAGE_500},
                503: {"description": ERROR_MESSAGE_503}
            })
def auth_check():
    """
        Validates authorization check from the access token
    :return: str
        The output will contain 200 OK if auth check is successful else it will return 403 Forbidden
    """
    return {"message": "OK"}
