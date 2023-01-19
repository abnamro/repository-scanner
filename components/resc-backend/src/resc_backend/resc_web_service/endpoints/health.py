# Standard Library
import logging

# Third Party
from fastapi import APIRouter, status

# First Party
from resc_backend.constants import ERROR_MESSAGE_500, ERROR_MESSAGE_503, HEALTH_TAG, RWS_ROUTE_HEALTH

router = APIRouter(tags=[HEALTH_TAG])

logger = logging.getLogger(__name__)


@router.get(f"{RWS_ROUTE_HEALTH}",
            summary="Health check",
            description="Retrieve the health status of RESC APIs",
            status_code=status.HTTP_200_OK,
            responses={
                200: {"description": "Retrieve the health status"},
                500: {"description": ERROR_MESSAGE_500},
                503: {"description": ERROR_MESSAGE_503}
            })
def health_check():
    return {"status": "OK"}
