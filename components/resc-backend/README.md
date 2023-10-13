# Repository Scanner Backend (RESC-Backend)
[![Python][python-shield]][python-url]
[![FastAPI][fast-api-shield]][fast-api-url]
[![SQLAlchemy][sqlalchemy-shield]][sqlalchemy-url]
[![Celery][celery-shield]][celery-url]
[![Pydantic][pydantic-shield]][pydantic-url]
[![RabbitMQ][rabbitmq-shield]][rabbitmq-url]
[![Redis][redis-shield]][redis-url]
[![Azure SQL Edge][database-shield]][database-url]
[![CI][ci-shield]][ci-url]
[![SonarCloud][sonar-cloud-shield]][sonar-cloud-url]


<!-- TABLE OF CONTENTS -->
## Table of contents
1. [About the component](#about-the-component)
2. [Getting started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Run RESC Web service locally from source](#run-resc-web-service-locally-from-source)
    - [Run RESC Web service locally through Make](#run-resc-web-service-locally-through-make)
    - [Run locally using docker](#run-locally-using-docker)
3. [Testing](#testing)
    - [Run unit tests, linting and import checks locally](#run-unit-tests-linting-and-import-checks-locally)
    - [Run Newman tests locally](#run-newman-tests-locally)
    - [Run OWASP ZAP API Security tests locally](#run-owasp-zap-api-security-tests-locally)
4. [Create a migration for database changes](#create-a-migration-for-database-changes)
    - [Use Alembic to create a new migration script](#use-alembic-to-create-a-new-migration-script)
    - [Use the --autogenerate parameter](#use-the---autogenerate-parameter)
    - [Running migration and rollback](#running-migration-and-rollback)
5. [Documentation](#documentation)

<!-- ABOUT THE COMPONENT -->
## About the component
The RESC-backend component includes database models, RESC Web service, Alembic scripts for database migration, RabbitMQ users, and queue creation.

<!-- GETTING STARTED -->
## Getting started

These instructions will help you to get a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites
- [Git](https://git-scm.com/downloads)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Python (v3.9.0 or higher)](https://www.python.org/downloads/release/python-390/)
- Install odbc 17 sql server driver for your OS
  * [Download for Windows](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server?view=sql-server-ver16#version-17)  
  * [Download for Mac](https://learn.microsoft.com/en-us/sql/connect/odbc/linux-mac/install-microsoft-odbc-driver-sql-server-macos?view=sql-server-ver16#17)  
  * [Download for Linux](https://learn.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server?view=sql-server-ver16#17)  `sudo apt install unixodbc-dev`


### Run RESC Web service locally
#### Run RESC Web service locally from source

<details>
  <summary>Preview</summary>
  Ensure resc database is up and running locally. </br>
  You can connect RESC web service to database, if you have already deployed RESC through helm in Kubernetes.</br>
  Open the Git Bash terminal from /components/resc-backend folder and run below commands.

  #### Create virtual environment:
  ```bash
  pip install virtualenv
  virtualenv venv
  source venv/Scripts/activate
  ```
 #### Install resc_backend package:
  ```bash
  pip install pyodbc==4.0.32
  pip install -e .
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

  Open http://127.0.0.1:8000 in a browser to access the API.
</details>

#### Run RESC Web service locally through make

*Note:* This procedure has been only tested in Linux and Mac. It may not work in machines running the Apple M1 chip due to lack of support from MSSQL docker image.  


Prerequisites: 
- Install [Make](https://www.gnu.org/software/make/) on your system.  
- Update MSSQL_PASSWORD (password you want to set for local database) in db.env file.

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

   This target will run a local MSSQL instance in a container called *resc-db*. It creates and populates the resc database schema using alembic and the sql script located in `test_data/database_dummy_data.sql`

   *Note:*: This target will also try to remove the DB container if it already exists.

   If you want to remove this container, run: `make cleandb`
  
3. Run Web service: 
  ```bash
  make rws
  ```
  Open http://127.0.0.1:1234 in a browser to access the API.

4. Clean up:
```bash
make clean
```
</details>

#### Run locally using docker
<details>
  <summary>Preview</summary>
  Run the RESC-Backend docker image locally with the following commands:

- Pull the docker image from registry:  
```bash
docker pull rescabnamro/resc-backend:latest
```

- Alternatively, build the docker image locally by running following command:
  Ensure resc database is up and running locally. </br>
  You can connect RESC web service to database, if you have already deployed RESC through helm in Kubernetes.</br>

  Open the Git Bash terminal from /components/resc-backend folder and run below commands.  
  Update MSSQL_PASSWORD value in the docker run command.  

```bash
docker build -t rescabnamro/resc-backend:latest .
```

- Use the following command to run the RESC backend: 
```bash
source db.env
docker run -p 8000:8000 -e DB_CONNECTION_STRING -e MSSQL_ODBC_DRIVER -e MSSQL_USERNAME -e RESC_REDIS_CACHE_ENABLE -e AUTHENTICATION_REQUIRED -e MSSQL_DB_HOST="host.docker.internal" -e MSSQL_PASSWORD="<enter password for local database>" -e MSSQL_SCHEMA="master" -e MSSQL_DB_PORT=30880 --name resc-backend rescabnamro/resc-backend:latest uvicorn resc_backend.resc_web_service.api:app --workers 1 --host 0.0.0.0 --port 8000
```

Open http://127.0.0.1:8000 in a browser to access the API.
</details>

## Testing
[(Back to top)](#table-of-contents)

### Run unit tests, linting and import checks locally:
See below commands for running various (unit/linting) tests locally. To run these tests you need to install [tox](https://pypi.org/project/tox/). This can be done on Linux and Windows with Git Bash.

Run below commands to make sure that the unit tests are running and that the code matches quality standards:
```bash
pip install tox      # install tox locally

tox -v -e sort       # Run this command to validate the import sorting
tox -v -e lint       # Run this command to lint the code according to this repository's standard
tox -v -e pytest     # Run this command to run the unit tests
tox -v               # Run this command to run all of the above tests
```

### Run Newman tests locally:
If you don't provide any argument to the script, then the default image value will be used    
```bash
cd tests/newman_tests
./run_newman_tests.sh
```

If you can override the images by providing below arguments to the script.
```bash
cd tests/newman_tests
./run_newman_tests.sh -b <resc-backend image:tag> -d <resc-database image:tag>  -n <newman image:tag> 

Example: ./run_newman_tests.sh -b 'rescabnamro/resc-backend:latest' -d 'mcr.microsoft.com/azure-sql-edge:1.0.7' -n 'postman/newman:5.3.1-alpine'
```

### Run OWASP ZAP API Security tests locally:
If you don't provide any argument to the script, then the default image value will be used
```bash
cd tests/zap_tests
./run_run_zap_api_tests.sh
```

If you can override the images by providing below arguments to the script.
```bash
cd tests/zap_tests
./run_run_zap_api_tests.sh -b <resc-backend image:tag> -d <resc-database image:tag>  -z <zap image:tag>

Example: ./run_newman_tests.sh -b 'rescabnamro/resc-backend:latest' -d 'mcr.microsoft.com/azure-sql-edge:1.0.7' -n 'owasp/zap2docker-weekly'
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


The generated script contains two functions:

- The upgrade function that contains the revision changes.
- The downgrade function that revert these changes.

</details>
&nbsp

### Use the --autogenerate parameter

<details>
  <summary>Preview</summary>
Alembic provide an --autogenerate parameter to help revision scripts creation. It can output the necessary changes to apply,  by comparing the current database schema
and the model stated in Python. To create that revision make sure you have a connection to a running database with an up-to-date schema version.

```bash
alembic revision --autogenerate -m "<revision summary>"
```
_**Note:**_ Autogenerate cannot detect all the required changes.The created revision script must be carefully checked and tested.
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
  _**Note:**_ A list of needed changes and a table containing alembic revision history are created during the first revision.


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

- [Alembic documentation](https://alembic.sqlalchemy.org/en/latest/index.html)

- [Connect to database using Azure Data Studio](https://learn.microsoft.com/en-us/sql/azure-data-studio/quickstart-sql-server?view=sql-server-ver16)

- [How to create a connection string](https://docs.sqlalchemy.org/en/14/core/engines.html)

- [Connect and view the database tables from Intellij IDEA Ultimate edition](https://www.jetbrains.com/help/idea/db-tutorial-connecting-to-ms-sql-server.html#connect-by-using-sql-server-authentication)


<!-- MARKDOWN LINKS & IMAGES -->
[python-shield]: https://img.shields.io/badge/Python-3670A0?style=flat&logo=python&logoColor=ffdd54
[python-url]: https://www.python.org
[fast-api-shield]: https://img.shields.io/badge/FastAPI-009688.svg?style=flat&logo=FastAPI&logoColor=white
[fast-api-url]: https://fastapi.tiangolo.com
[sqlalchemy-shield]: https://img.shields.io/badge/SQLAlchemy-306998?logo=python&logoColor=white
[sqlalchemy-url]: https://fastapi.tiangolo.com
[celery-shield]: https://img.shields.io/badge/Celery-green.svg?logo=celery&style=flat
[celery-url]: https://docs.celeryq.dev
[pydantic-shield]: https://img.shields.io/badge/Pydantic-e92063.svg?logo=pydantic&style=flat
[pydantic-url]: https://docs.pydantic.dev
[rabbitmq-shield]: https://img.shields.io/badge/RabbitMQ-%23FF6600.svg?&style=flat&logo=RabbitMQ&logoColor=white
[rabbitmq-url]: https://www.rabbitmq.com
[redis-shield]: https://img.shields.io/badge/Redis-%23DD0031.svg?&style=flat&logo=Redis&logoColor=white
[redis-url]: https://redis.com/ 
[ci-shield]: https://img.shields.io/github/actions/workflow/status/abnamro/repository-scanner/backend-ci.yaml?logo=github
[database-shield]: https://img.shields.io/badge/Azure%20SQL%20Edge-blue?logo=microsoftazure
[database-url]: https://azure.microsoft.com/en-us/services/sql-edge
[ci-url]: https://github.com/abnamro/repository-scanner/actions/workflows/backend-ci.yaml
[sonar-cloud-shield]: https://sonarcloud.io/api/project_badges/measure?project=abnamro-resc_resc-backend&metric=alert_status
[sonar-cloud-url]: https://sonarcloud.io/summary/new_code?id=abnamro-resc_resc-backend
  
