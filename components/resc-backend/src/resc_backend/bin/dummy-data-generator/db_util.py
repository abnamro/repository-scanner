# Standard Library
import logging
import sys

# Third Party
import pyodbc
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

# First Party
from resc_backend.common import initialise_logs
from resc_backend.constants import LOG_FILE_DUMMY_DATA_GENERATOR
from resc_backend.db.connection import Session, engine
from resc_backend.db.model import Base

CONNECTION_CHECK_QUERY = text("select 1 from finding")
RESC_DB_MODEL_MODULE = "resc_backend.db.model"

logger_config = initialise_logs(LOG_FILE_DUMMY_DATA_GENERATOR)
logger = logging.getLogger(__name__)


class DbUtil:
    """Contains all the utilities required to communicate with the database."""

    def __init__(self):
        self.session = Session(bind=engine)

    def is_db_connected(self) -> bool:
        try:
            self.session.execute(CONNECTION_CHECK_QUERY)
            logger.info("Connected to database.")
            return True
        except (DBAPIError, pyodbc.Error) as err:
            logger.error(f"[{err}]")
            return False

    def clear_db_tables(self):
        try:
            logger.info("Dropping all tables")
            Base.metadata.drop_all(bind=engine)
            logger.info("Creating all tables")
            Base.metadata.create_all(bind=engine)
        except pyodbc.Error as err:
            self.handle_and_exit(err)

    def persist_data(self, data: list):
        try:
            self.session.add_all(data)
            self.session.commit()
        except pyodbc.Error as err:
            self.handle_and_exit(err)

    def bulk_persist_data(self, klass: Base, data: list[dict]):
        try:
            self.session.bulk_insert_mappings(klass, data)
            self.session.commit()
        except pyodbc.Error as err:
            self.handle_and_exit(err)

    def handle_and_exit(self, err):
        logger.error(f"An error occurred: [{err}]")
        logger.error("Rolling back the changes and exiting.")
        self.session.rollback()
        self.shut_down()
        sys.exit(-1)

    def shut_down(self):
        try:
            if not self.session.close():
                self.session.close()
                logger.info("Closed session.")
            if not self.session.connection().invalidated:
                self.session.connection().invalidate()
                logger.info("Invalidated connection.")
            engine.dispose()
            logger.debug("Engine disposed.")
        except pyodbc.Error as err:
            logger.error(f"[{err}]")

    def get_data_for_single_attr(self, klass: Base, attr: str):
        """Generic way to retrieve a list of values from the database. These values will be fetched based on the
         specified attribute of the class 'klass'.
         ex: id_, name, version"""
        try:
            return [r[0] for r in self.session.query(klass.__getattribute__(klass, attr))]
        except AttributeError as ex:
            logger.error(f"{klass} does not have any attribute [{attr}].")
            self.handle_and_exit(ex)
        except pyodbc.Error as err:
            self.handle_and_exit(err)

    def get_data_for_multiple_attr(self, table, columns):
        try:
            return self.session.query(*(getattr(table, column) for column in columns)).all()
        except AttributeError as ex:
            logger.error(f"{table} does not have the one more attributes in the attribute list.")
            self.handle_and_exit(ex)
        except pyodbc.Error as err:
            self.handle_and_exit(err)
