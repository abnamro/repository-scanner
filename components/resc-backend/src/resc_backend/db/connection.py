# pylint: disable=C0413
# Standard Library
import logging
import os

# Third Party
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# First Party
from resc_backend.db.model import Base

basedir = os.path.abspath(os.path.dirname(__file__))
logger = logging.getLogger(__name__)

DB_CONNECTION_STRING = os.environ.get("DB_CONNECTION_STRING")
try:
    DB_CONNECTION_STRING = DB_CONNECTION_STRING.format(**os.environ)
except AttributeError:
    logger.warning("Missing DB Connection environment variables, using SQLite database")
    DB_CONNECTION_STRING = ""
SQL_ALCHEMY_POOL_SIZE_DEFAULT = 25
SQL_ALCHEMY_MAX_OVERFLOW_DEFAULT = 15

echo_queries = os.getenv('SQL_ALCHEMY_ECHO_QUERIES', 'False').lower() in ('true', '1', 'y')
pool_size = int(os.environ.get("SQL_ALCHEMY_POOL_SIZE", SQL_ALCHEMY_POOL_SIZE_DEFAULT))
max_overflow = int(os.environ.get("SQL_ALCHEMY_MAX_OVERFLOW", SQL_ALCHEMY_MAX_OVERFLOW_DEFAULT))

if DB_CONNECTION_STRING:
    logger.info("Using provided environment variable to connect to the Database")
    engine = create_engine(DB_CONNECTION_STRING, echo=echo_queries, pool_size=pool_size, max_overflow=max_overflow)
else:
    DATABASE_URL = 'sqlite:///' + os.path.join(basedir, 'db.sqlite?check_same_thread=False')
    logger.info(f"Database environment variables were not provided, defaulting to {DATABASE_URL}")
    engine = create_engine(DATABASE_URL, echo=echo_queries)
    Base.metadata.create_all(engine, checkfirst=True)

Session = sessionmaker()
