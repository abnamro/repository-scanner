import inspect
import logging
import sys

from sqlalchemy.exc import DBAPIError
from sqlalchemy.sql import select

from resc_backend.common import initialise_logs
from resc_backend.constants import LOG_FILE_DUMMY_DATA_GENENERATOR
from resc_backend.db.connection import Session, engine
from resc_backend.db.model import Base

CONNECTION_CHECK_QUERY = "select 1 from finding"
RESC_DB_MODEL_MODULE = "resc_backend.db.model"

logger_config = initialise_logs(LOG_FILE_DUMMY_DATA_GENENERATOR)
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
        except (DBAPIError, Exception) as ex:
            logger.error(f"[{ex}]")
            return False

    def clear_db_tables(self):
        table_model = {}
        cls_members = inspect.getmembers(sys.modules[RESC_DB_MODEL_MODULE], inspect.isclass)
        logger.info(f"Found [{len(cls_members)}] models.")
        for mapper in Base.registry.mappers:
            model = mapper.class_
            table_model[model.__tablename__] = model
        # an ordered sequence of tables to be dropped is required
        # as in RESC db model CASCADE DROP has not been enabled.
        # Hence, looping over the models and attempting to delete
        # would fail. So, this has to be done manually.
        model_drop_order = [table_model.get("rule_tag"),
                            table_model.get("scan_finding"),
                            table_model.get("finding"),
                            table_model.get("audit"),
                            table_model.get("scan"),
                            table_model.get("rules"),
                            table_model.get("rule_pack"),
                            table_model.get("rule_allow_list"),
                            table_model.get("repository"),
                            table_model.get("tag"),
                            table_model.get("vcs_instance")]
        for model in model_drop_order:
            try:
                logger.info(f"Attempting to clear [{model.__tablename__}]")
                self.session.query(model).delete()
                self.session.commit()
            except Exception as ex:
                self.handle_exception_and_exit(ex)

    def persist_data(self, data: list):
        try:
            self.session.add_all(data)
            self.session.commit()
        except Exception as ex:
            self.handle_exception_and_exit(ex)

    def handle_exception_and_exit(self, ex):
        logger.error(f"An exception occured: [{ex}]")
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
        except Exception as ex:
            logger.error(f"[{ex}]")

    def get_data_for_single_attr(self, klass: Base, attr: str):
        """Generic way to retrieve a list of values from the database. These values will be fetched based on the 
         specified attribute of the class 'klass'.
         ex: id_, name, version"""
        try:
            return [r.__getitem__(attr) for r in self.session.query(klass.__getattribute__(klass, attr))]
        except AttributeError as ex:
            logger.error(f"{klass} does not have any attribute [{attr}].")
            self.handle_exception_and_exit(ex)
        except Exception as ex:
            self.handle_exception_and_exit(ex)

    def get_data_for_multiple_attr(self, table, columns):
        try:
            return self.session.query(*(getattr(table, column) for column in columns)).all()
        except AttributeError as ex:
            logger.error(f"{table} does not have the one more attributes in the attribute list.")
            self.handle_exception_and_exit(ex)
        except Exception as ex:
            self.handle_exception_and_exit(ex)
