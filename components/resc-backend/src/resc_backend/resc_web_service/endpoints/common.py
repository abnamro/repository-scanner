# Standard Library
from typing import List

# Third Party
from fastapi import APIRouter, Response, status

# First Party
from resc_backend.constants import CACHE_MAX_AGE, COMMON_TAG, RWS_ROUTE_AUTH_CHECK, RWS_ROUTE_SUPPORTED_VCS_PROVIDERS
from resc_backend.resc_web_service.schema.vcs_provider import VCSProviders

router = APIRouter(tags=[COMMON_TAG])


@router.get(f"{RWS_ROUTE_SUPPORTED_VCS_PROVIDERS}",
            response_model=List[str],
            status_code=status.HTTP_200_OK,
            responses={
                200: {"description": "Retrieve the supported vcs-providers"}
            })
def get_supported_vcs_providers(response: Response) -> List[str]:
    """
        Retrieve all supported vcs providers
    :return: List[str]
        The output will contain a list of strings of unique rules in the findings table
    """
    response.headers["Cache-Control"] = CACHE_MAX_AGE
    supported_vcs = [vcs for vcs in VCSProviders if vcs]
    return supported_vcs


@router.get(f"{RWS_ROUTE_AUTH_CHECK}",
            status_code=status.HTTP_200_OK,
            responses={
                200: {"description": "Validate authorization check from the access-token"}
            })
def auth_check():
    """
        Validates authorization check from the access token
    :return: str
        The output will contain 200 OK if auth check is successful else it will return 403 Forbidden
    """
    return {"message": "OK"}
