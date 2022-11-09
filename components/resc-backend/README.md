# Repository Scanner Backend (RESC-Backend)

<!-- TABLE OF CONTENTS -->
## Table of Contents
1. [About The Component](#about-the-component)
2. [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Run RESC Web service locally from source](#run-resc-web-service-locally-from-source)
    - [Run RESC Web service locally through make](#run-resc-web-service-locally-through-make)
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
- [Git](https://git-scm.com/downloads)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Python 3.9.0](https://www.python.org/downloads/release/python-390/)
- Install odbc 17 sql server driver for your OS
  * [Download for Windows](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server?view=sql-server-ver16#version-17)  
  * [Download for Mac](https://learn.microsoft.com/en-us/sql/connect/odbc/linux-mac/install-microsoft-odbc-driver-sql-server-macos?view=sql-server-ver16#17)  
  * [Download for Linux](https://learn.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server?view=sql-server-ver16#17)  `sudo apt install unixodbc-dev`


### Run RESC Web service locally
#### Run RESC Web service locally from source

<details>
  <summary>Preview</summary>
  Ensure resc database is up and running locally. </br>
  If you have alreday deployed RESC through helm in Kubernetes, then you can connect RESC web service to database.</br>
  Open git bash terminal from /components/resc-backend folder and run below commands.

  #### Create virtual environment:
  ```bash
  pip install virtualenv
  virtualenv venv
  source venv/Scripts/activate
  ```
 #### Install resc_backend package:
  ```bash
  pip install pyodbc==4.0.32
  pip install -e 
  ```
 #### Set environment variables:
  ```bash
  source db.env
  export MSSQL_SCHEMA=master
  export MSSQL_DB_PORT=30880
  export MSSQL_PASSWORD="<enter password for local database>"
  ```
  #### Run Web service:
  ```bash
  uvicorn resc_backend.resc_web_service.api:app --workers 1
  ```

  Open http://127.0.0.1:8000 in browser to access the api.
</details>
&nbsp

#### Run RESC Web service locally through make
*Note:* This has ben only tested in Linux and Mac. This may not work in Apple M1 chip due to lack of support from MSSQL docker image.  

Prerequisites: 
1. Install make on your system.  
2. Update MSSQL_PASSWORD (password you want to set for local database) in db.env file.

<details>
  <summary>Preview</summary>

1. Create Python virtual environment and install resc_backend package:
  ```bash
  make env
  ```

2. Run database locally:
  ```bash
  make db
  ```

   This target will run a local MSSQL instance in a container called *resc-db* and create and populate the resc database schema using alembic and the sql script located in `test_data/database_dummy_data.sql`

   ***Note***: This target will also try to remove the DB container if it already exists.

   If you want to remove this container you can run: `make cleandb`
  
3. Run Web service: 
  ```bash
  make rws
  ```
  Open http://127.0.0.1:1234 in browser to access the api.

4. Clean up:
```bash
make clean
```
</details>
&nbsp

#### Run locally using docker
<details>
  <summary>Preview</summary>
  Build the RESC Backend docker image locally by running the following commands:

- Pull the docker image from registry:  
```bash
docker pull ghcr.io/abnamro/resc-backend:0.0.1
```

- Alternatively, build the docker image locally by running following command:
  Ensure resc database is up and running locally. </br>
  If you have alreday deployed RESC through helm in Kubernetes, then you can connect RESC web service to database.</br>

  Open git bash terminal from /components/resc-backend folder and run below commands.  
  Update MSSQL_PASSWORD value in the docker run command.  

```bash
docker build -t ghcr.io/abnamro/resc-backend:0.0.1 .
```

- Run the RESC backend by using the following command: 
```bash
source db.env
docker run -p 8000:8000 -e DB_CONNECTION_STRING -e MSSQL_ODBC_DRIVER -e MSSQL_USERNAME -e AUTHENTICATION_REQUIRED -e MSSQL_DB_HOST="host.docker.internal" -e MSSQL_PASSWORD="<enter password for local database>" -e MSSQL_SCHEMA="master" -e MSSQL_DB_PORT=30880 --name resc-backend ghcr.io/abnamro/resc-backend:0.0.1 uvicorn resc_backend.resc_web_service.api:app --workers 1 --host 0.0.0.0 --port 8000
```

Open http://127.0.0.1:8000 in browser to access the api.
</details>
&nbsp

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
<details>
  <summary>Preview</summary>
This command will create a new revision script in the ./alembic/versions directory

```bash
alembic revision -m "<revision summary>"
```
The filename is prefixed with the revision identifier used by Alembic to keep track of the revision history.
Make sure that the down_revision variable contains the identifier of the previous revision.
For instance:

```bash
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
</details>
&nbsp

### Use the --autogenerate parameter

<details>
  <summary>Preview</summary>
Alembic provide an --autogenerate parameter to help revision scripts creation. By comparing the current database schema
and the model stated in python, it can output the necessary changes to apply. To create that revision make sure you have
a connection to a running database with a up-to-date schema version.

```bash
alembic revision --autogenerate -m "<revision summary>"
```
However, autogenerate cannot detect all the required changes and therefore the created revision script has to be
carefully checked and tested.
</details>
&nbsp

### Running migration and rollback
<details>
  <summary>Preview</summary>
  To upgrade/downgrade the database schema use the following:

  ```bash
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
  ```bash
  alembic current
  ```

  And the revision history:
  ```bash
  alembic history --verbose
  ```
</details>
&nbsp

## Documentation
[(Back to top)](#table-of-contents)

[Alembic documentation](https://alembic.sqlalchemy.org/en/latest/index.html)

[Connect to database using Azure Data Studio](https://learn.microsoft.com/en-us/sql/azure-data-studio/quickstart-sql-server?view=sql-server-ver16)

[How to create a connection string](https://docs.sqlalchemy.org/en/14/core/engines.html)

[To connect and view the database tables from Intellij IDEA Ultimate edition](https://www.jetbrains.com/help/idea/db-tutorial-connecting-to-ms-sql-server.html#connect-by-using-sql-server-authentication)
  
