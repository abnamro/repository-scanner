# pylint: disable=C0413
# Standard Library
import logging
import os
import struct

# Third Party
from azure.identity import DefaultAzureCredential
from sqlalchemy import create_engine

basedir = os.path.abspath(os.path.dirname(__file__))
logger = logging.getLogger(__name__)


def create_azure_engine(connection_string: str, echo_queries: bool, pool_size: int, max_overflow: int):
    """
        Create a SQLAlchemy Engine with added azure token injection
    :param connection_string:
        the connection string to the database
    :param echo_queries:
        bool, echo queries as defined in SQLAlchemy
    :param pool_size:
        integer, pool size as defined in SQLAlchemy
    :param max_overflow:
        integer, max overflow as defined in SQLAlchemy
    :return: SQLAlchemyEngine
        The output will contain the engine
    """

    managed_identity_client_id = os.environ.get("MANAGED_IDENTITY_CLIENT_ID")
    if not managed_identity_client_id:
        logger.error("Missing environment variable MANAGED_IDENTITY_CLIENT_ID")
    credential = DefaultAzureCredential(managed_identity_client_id=managed_identity_client_id)

    # Get token for Azure SQL Database and convert to UTF-16-LE for SQL Server driver
    token = credential.get_token("https://database.windows.net/.default").token.encode("UTF-16-LE")
    token_struct = struct.pack(f'<I{len(token)}s', len(token), token)

    sql_copt_ss_access_token = 1256

    logger.info("Using provided environment variable to connect to the Database with azure token auth")
    engine = create_engine(connection_string, echo=echo_queries, pool_size=pool_size, max_overflow=max_overflow,
                           connect_args={'attrs_before': {sql_copt_ss_access_token: token_struct}})
    return engine
