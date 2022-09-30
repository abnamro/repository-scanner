# pylint: disable=C0413,W0611,W0404
# Standard Library
import logging.config
import os

# Third Party
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
from starlette.status import HTTP_302_FOUND
from tenacity import RetryError

# First Party
from resc_backend.constants import RWS_VERSION_PREFIX
from resc_backend.db.connection import Session, engine
from resc_backend.resc_web_service.dependencies import (
    check_db_initialized,
    requires_auth,
    requires_no_auth
)
from resc_backend.resc_web_service.endpoints import (
    branches_info,
    common,
    detailed_findings,
    findings,
    health,
    repositories_info,
    rules,
    scans,
    vcs_instances
)


def generate_logger_config(log_file_path, debug=True):
    """A function to generate the global logger config dictionary

    Arguments:
        log_file_path {string} -- Path where the logs are to be stored

    Keyword Arguments:
        debug {bool} -- Whether the logging level should be set to DEBUG or INFO (default: {True})

    Returns:
        Dict -- A dictionary containing the logger configuration
    """

    logging_level = "DEBUG" if debug else "INFO"
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "generic-log-formatter": {
                "format": "[%(levelname)s] [%(name)s] [%(asctime)s] %(message)s"
            },
        },
        "handlers": {
            "console": {
                "level": logging_level,
                "class": "logging.StreamHandler",
                "formatter": "generic-log-formatter",
            },
            "file": {
                "level": logging_level,
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "generic-log-formatter",
                "filename": log_file_path,
                "maxBytes": 100 * 1024 * 1024,
                "backupCount": 5
            }
        },
        "loggers": {
            "": {
                "handlers": ["console", "file"],
                "level": logging_level,
                "propagate": True
            },
        }
    }

    return logging_config


logging.config.dictConfig(generate_logger_config('local_logs.log'))
logger = logging.getLogger(__name__)
tags_metadata = [
    {"name": "health", "description": "Checks health for API"},
    {"name": "resc-common", "description": "Manage common information"},
    {"name": "resc-rules", "description": "Manage rule information"},
    {"name": "resc-repositories", "description": "Manage repository information"},
    {"name": "resc-branches", "description": "Manage branch information"},
    {"name": "resc-scans", "description": "Manage scan information"},
    {"name": "resc-findings", "description": "Manage findings information"},
    {"name": "resc-vcs-instances", "description": "Manage vcs instance information"},
]

# Check if authentication is required for api endpoints
AUTH = [Depends(requires_no_auth)] if os.getenv('AUTHENTICATION_REQUIRED', '') == 'false' else [Depends(requires_auth)]

app = FastAPI(title="Repository Scanner(RESC)",
              description="RESC API helps you to perform several operations upon findings "
                          "obtained from multiple source code repositories.",
              openapi_tags=tags_metadata, dependencies=AUTH)

if os.getenv('ENABLE_CORS', '') == 'true':
    origins = os.getenv('CORS_ALLOWED_DOMAINS', '').split(', ')
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(health.router, prefix=RWS_VERSION_PREFIX)
app.include_router(common.router, prefix=RWS_VERSION_PREFIX)
app.include_router(branches_info.router, prefix=RWS_VERSION_PREFIX)
app.include_router(rules.router, prefix=RWS_VERSION_PREFIX)
app.include_router(findings.router, prefix=RWS_VERSION_PREFIX)
app.include_router(detailed_findings.router, prefix=RWS_VERSION_PREFIX)
app.include_router(repositories_info.router, prefix=RWS_VERSION_PREFIX)
app.include_router(scans.router, prefix=RWS_VERSION_PREFIX)
app.include_router(vcs_instances.router, prefix=RWS_VERSION_PREFIX)


@app.on_event("startup")
def app_startup():
    try:
        _ = Session(bind=engine)
        check_db_initialized()

        logger.info("Database is connected, expected table(s) found")
    except RetryError as exc:
        raise SystemExit("Error while connecting to the database, retry timed out") from exc


@app.get("/")
def view_docs():
    return RedirectResponse(url="/docs", status_code=HTTP_302_FOUND)
