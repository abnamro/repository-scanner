# Standard Library
import logging
import os
from logging.config import fileConfig
from logging import INFO

# Third Party
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

logger = logging.getLogger()

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
from resc_backend.db.model import Base
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.
DB_CONNECTION_STRING = os.environ.get("DB_CONNECTION_STRING")
try:
    DB_CONNECTION_STRING = DB_CONNECTION_STRING.format(**os.environ)
except AttributeError:
    logger.warning("Missing DB Connection environment variables, using SQLite database")
    DB_CONNECTION_STRING = ""
db_url_escaped = DB_CONNECTION_STRING.replace('%', '%%')
config.set_main_option("sqlalchemy.url", db_url_escaped)


def get_current_revision():
    return context.get_context().get_current_revision()


def get_head_revision():
    return context.get_head_revision()


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        literal_binds=True,
        target_metadata=target_metadata,
        compare_type=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True
        )

        # Log info regarding current revision status
        if logger.isEnabledFor(INFO):
            current_revision = get_current_revision()
            logger.info(f"Current revision: {current_revision}")
            if current_revision == get_head_revision():
                logger.info(f"{current_revision} is latest")

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
