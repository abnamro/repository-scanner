# Repository Scanner Backend (RESC-Backend)

<!-- TABLE OF CONTENTS -->
## Table of Contents
1. [About The Component](#about-the-component)
2. [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Run locally from source](#run-locally-from-source)
    - [Run locally using docker](#run-locally-using-docker)
3. [Testing](#testing)
4. [Create a migration for database changes](#create-a-migration-for-database-changes)
    - [Use Alembic to create a new migration script](#use-alembic-to-create-a-new-migration-script)
    - [Use the --autogenerate parameter](#use-the---autogenerate-parameter)
    - [Running migration and rollback](#running-migration-and-rollback)
5. [Documentation](#documentation)

<!-- ABOUT THE COMPONENT -->
## About The Component
The RESC-BACKEND component includes Database models, RESC Web service, Alembic scripts for database migration and RabbitMQ users and queue creation.

<!-- GETTING STARTED -->
## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites
- Install Docker Desktop
- Install [Python 3.9.0](https://www.python.org/downloads/release/python-390/)

**For Deploying the RESC Web Service locally:**
- Local automated deployment rely on a Makefile, so first you need to install make:
  ```
  brew install make
  ```

**For Deploying the database locally:**
- To locally deploy the database associated with RESC it is key that you first install the odbc 17 sql server driver. On Linux you do this by running the following command:  
```
sudo apt install unixodbc-dev
```
- If you're on a Windows machine, visit the following [link](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server?view=sql-server-ver16):  
- If you're on a different OS, visit the following [link](https://learn.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server?view=sql-server-ver16#17):  
- Upon installing the driver, it is important that you properly set the following environment variables in the `db.env` file. Not doing so will result in an error in the database/not being able to load it properly.

  MSSQL_PASSWORD : Password for local database

### Run locally from source

Clone the repository and install the resc_backend package locally:
```
git clone -b <branch-name> <repository-scanner repo url>
cd components/resc-backend
pip install -e .
```

1. For Running the RESC Web Service:

    1. Create Python virtual environment: `venv`
    2. Install repository_scanner_backend using: `make env`
    3. Then you can run the STS api by running: `make sts`


2. For Deploying the database locally, run the following command:
   `make db`

   This target will run a local MSSQL instance in a container called *resc-db* and create and populate the resc database schema using alembic and the sql script located in `test_data/database_dummy_data.sql`

   ***Note***: This target will also try to remove the DB container if it already exists.

   If you want to remove this container you can run: `make cleandb`

### Run locally using docker

Build the RESC Backend docker image locally by running the following commands (Keep the image version parameter in mind):

- Pull the docker image from registry:  
```
docker pull ghcr.io/abnamro/resc-backend:0.0.1
```
- Alternatively, build the docker image locally by running following command:
```
cd repository-scanner/components/resc-backend
docker build -t ghcr.io/abnamro/resc-backend:0.0.1 .
```
- Run the RESC backend by using the following command: 
```
docker run --name resc-backend ghcr.io/abnamro/resc-backend:0.0.1
```

## Testing
[(Back to top)](#table-of-contents)

In order to run (unit/linting) tests locally, there are several command specified below on how to run these tests.
To run these tests you need to install tox this can be done on Linux and Windows, where or the latter you can use GIT Bash.

To make sure the unit tests are running and that the code matches quality standards run:
```
pip install tox      # install tox locally

tox -v -e sort       # Run this command to validate the import sorting
tox -v -e lint       # Run this command to lint the code according to this repository's standard
tox -v -e -e pytest  # Run this command to run the unit tests
tox -v               # Run this command to run all of the above tests
```

## Create a migration for database changes
[(Back to top)](#table-of-contents)

### Use Alembic to create a new migration script

This command will create a new revision script in the ./alembic/versions directory
```
alembic revision -m "<revision summary>"
```
The filename is prefixed with the revision identifier used by Alembic to keep track of the revision history.
Make sure that the down_revision variable contains the identifier of the previous revision.
For instance:

```
#d330d086edfe_first_revision.py
revision = 'd330d086edfe'
down_revision = None
...

#e653f899efgh_second_revision.py
revision = 'e653f899efgh'
down_revision = 'd330d086edfe'
```

The generated script contains two functions: The upgrade() function that contain the revision changes, and the
downgrade() function that revert these changes.

### Use the --autogenerate parameter

Alembic provide a --autogenerate parameter to help revision scripts creation. By comparing the current database schema
and the model stated in python, it can output the necessary changes to apply. To create that revision make sure you have
a connection to a running database with a up-to-date schema version
```
alembic revision --autogenerate -m "<revision summary>"
```
However, autogenerate cannot detect all the required changes and therefore the created revision script has to be
carefully checked and tested.

### Running migration and rollback

To upgrade/downgrade the database schema use the following:
```
# Upgrade to specified revision identifier
alembic upgrade <revision_identifier>

# Upgarde to latest
alembic upgrade head

# Upgrade to the next revision
alembic upgrade +1

# Run next revision from a specific revision
alembic upgrade <revision_identifier>+1

# Downgrade to base (no revision applied)
alembic downgrade base

# Downgrade to the previous revision
alembic downgrade -1
```
Note that during the first revision, in addition to changes to be made a table containing alembic revision history
will also be created.


You can also check current revision information:
```
alembic current
```

And the revision history:
```
alembic history --verbose
```


## Documentation
[(Back to top)](#table-of-contents)

[Alembic documentation](https://alembic.sqlalchemy.org/en/latest/index.html)

[How to create a connection string](https://docs.sqlalchemy.org/en/14/core/engines.html)

[To connect and view the tables from Intellij IDEA Ultimate edition](https://www.jetbrains.com/help/idea/db-tutorial-connecting-to-ms-sql-server.html#connect-by-using-sql-server-authentication)
  
