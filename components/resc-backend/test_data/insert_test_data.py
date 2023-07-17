# pylint: disable=C0413
# Standard Library
import logging
import os
import sys

# Third Party
import pyodbc

logging.basicConfig(level=logging.INFO)

REQUIRED_ENV_VARIABLES = ["MSSQL_DB_HOST", "MSSQL_DB_PORT", "MSSQL_SCHEMA", "MSSQL_USERNAME", "MSSQL_PASSWORD",
                          "MSSQL_ODBC_DRIVER"]
try:
    env_variables = {}
    missing_env_variables = []
    for var_name in REQUIRED_ENV_VARIABLES:
        value = os.getenv(var_name)
        if value is None:
            missing_env_variables.append(var_name)
        env_variables[var_name] = value
    if missing_env_variables:
        raise ValueError(f"The following env variables need to be set: {', '.join(missing_env_variables)}")

    MSSQL_DB_HOST = env_variables["MSSQL_DB_HOST"]
    MSSQL_DB_PORT = env_variables["MSSQL_DB_PORT"]
    MSSQL_SCHEMA = env_variables["MSSQL_SCHEMA"]
    MSSQL_USERNAME = env_variables["MSSQL_USERNAME"]
    MSSQL_PASSWORD = env_variables["MSSQL_PASSWORD"]
    MSSQL_ODBC_DRIVER = env_variables["MSSQL_ODBC_DRIVER"]
    MSSQL_DB_SERVER = f"{MSSQL_DB_HOST},{MSSQL_DB_PORT}"

    DB_CONNECTION_STRING = f"DRIVER={{{MSSQL_ODBC_DRIVER}}};SERVER={MSSQL_DB_SERVER};DATABASE={MSSQL_SCHEMA};" \
                           f"UID={MSSQL_USERNAME};PWD={MSSQL_PASSWORD};Encrypt=yes;TrustServerCertificate=yes"

    # Establish database connection
    conn = pyodbc.connect(DB_CONNECTION_STRING)
    cursor = conn.cursor()

    try:
        sql_file_path = 'test_data/database_dummy_data.sql'
        with open(sql_file_path, 'r') as sql_file:
            sql_script = sql_file.read()
        cursor.execute(sql_script)
        conn.commit()
        logging.info("Test data successfully inserted into database")
    except pyodbc.Error as ex:
        logging.error(f"Query execution failed while inserting test data: {ex}")
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()
except ValueError as ex:
    logging.error(f"Missing environment variables: {ex}")
    sys.exit(1)
except pyodbc.Error as ex:
    logging.error(f"Database connection error: {ex}")
    sys.exit(1)
except Exception as ex:
    logging.error(f"An error occurred while inserting test data: {ex}")
    sys.exit(1)
