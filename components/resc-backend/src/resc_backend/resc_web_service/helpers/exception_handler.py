from __future__ import annotations

# Standard Library
import logging

# Third Party
from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError

# First Party
from resc_backend.constants import ERROR_MESSAGE_500, ERROR_MESSAGE_503


def add_exception_handlers(app: FastAPI):
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        log_warning(request, exc, "422 Unprocessable Entity")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
        )

    @app.exception_handler(ValueError)
    async def value_error_exception_handler(request: Request, exc: ValueError):
        log_warning(request, exc, "400 Bad Request")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
        )

    @app.exception_handler(Exception)
    async def internal_server_error_exception_handler(request: Request, exc: Exception):
        log_error(request, exc, "500 Internal Server Error")
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            content={"detail": ERROR_MESSAGE_500})

    @app.exception_handler(OperationalError)
    async def service_unavailable_exception_handler(request: Request, exc: OperationalError):
        log_error(request, exc, "503 Service Unavailable")
        return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            content={"detail": ERROR_MESSAGE_503})


def log_error(request: Request, exc: Exception, response_status: str):
    """
        Send error details to log file
    :param request:
        Request object for the endpoint
    :param exc:
        Exception thrown by the endpoint
    :param response_status:
        Response status from the endpoint
    """
    logging.error(f"{request.method} {request.url} {response_status}")
    if hasattr(exc, "body"):
        logging.error(f"request body: {exc.body}")
    logging.error(f"error: {exc}")


def log_warning(request: Request, exc: Exception, response_status: str):
    """
        Send warning details to log file
    :param request:
        Request object for the endpoint
    :param exc:
        Exception thrown by the endpoint
    :param response_status:
        Response status from the endpoint
    """
    exc_str = f"{exc}".replace("\n", " ").replace("   ", " ")
    logging.warning(f"{request.method} {request.url} {response_status}")
    if hasattr(exc, "body"):
        logging.warning(f"request body: {exc.body}")
    logging.warning(f"warning: {exc_str}")
