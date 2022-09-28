# RESC
Repository Scanner framework

[![Backend basic validation](https://github.com/ABNAMRO/repository-scanner/actions/workflows/backend-basic-validation.yaml/badge.svg)](https://github.com/ABNAMRO/repository-scanner/actions/workflows/backend-basic-validation.yaml)

# Local Setup
Run the below command from project root folder if your IDE doesn't recognize repository_scanner_backend as a valid python package  
```
export PIP_CONFIG_FILE=pip.conf
pip install -e .
```

## Deploying the Secret Tracking Service API locally:

### Prerequisites

- Local automated deployment rely on a Makefile, so first you need to install make:
`brew install make`
- Make sure Docker is running locally

### Deploying the database locally:
In order to run the database on a local environment (macOS) you first need to install the mssql driver:
`brew install msodbcsql17`

You also need to set the following environment variables in the file `db.env`
MSSQL_PASSWORD : Password for local database
RULE_PACK_VERSION_TAG: Tag from resc-rules repository
VCS_ACCESS_TOKEN: Personal access token to clone resc-rules repository

Then run the following command:
`make db`

This target will run a local MSSQL instance in a container called *resc-db* and create and populate the resc database schema using alembic and the sql script located in `test_data/database_dummy_data.sql`
Note: this target will also try to remove the DB container if it already exists.


If you want to remove this container you can run: `make cleandb` 

### Running the Repository scanner Web service:
First you need to make sure the python virtual environment is created under `venv` and `repository_scanner_backend` is installed there using:
`make env`

Then you can run the RWS api by running: `make rws`

# Deployment
Deployment is done via Kubernetes, for local testing the easiest solution for this is enabling the kubernetes feature in Docker desktop and installing kubectl.


- Build the RESC base image locally by running the following command (base image version parameter defaults to 1.0.0): 
```
./rebuild.sh <base image version>
```
- If you are using Apple M1 Pro, then build the RESC docker image locally by running command 
```
./rebuild_for_AppleM1Pro.sh <base image version>
```
- Deploy locally by referring README section of resc-infra repository:  


#Testing
In order to run (unit/linting) tests locally, you can use the following commands:
* `make test` to run all tests.
* `export PIP_CONFIG_FILE=pip.conf && tox -e lint` for linting
* `export PIP_CONFIG_FILE=pip.conf && tox -e pytest` for unit testing
* `export PIP_CONFIG_FILE=pip.conf && tox -e sort` for detecting issues in the sorting (and in order to fix sorting just run: `isort src/ tests/`)

# Create a migration for database changes

## Use Alembic to create a new migration script

This command will create a new revision script in the ./alembic/versions directory
```
alembic revision -m "<revision summary>"
```
The filename is prefixed with the revision identifier used by Alembic to keep track of the revision history.
Make sure that the down_revision variable contains the identifier of the previous revision:
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

## Use the --autogenerate parameter

Alembic provide a --autogenerate parameter to help revision scripts creation. By comparing the current database schema
and the model stated in python, it can output the necessary changes to apply. To create that revision make sure you have
a connection to a running database with a up-to-date schema version
```
alembic revision --autogenerate -m "<revision summary>"
```
However, autogenerate cannot detect all the required changes and therefore the created revision script has to be 
carefully checked and tested.

## Running migration and rollback

To upgrade/downgrade the database schema use the following
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
will also be created


You can also check current revision information
```
alembic current
```

And the revision history
```
alembic history --verbose
```

## Generating migration scripts locally
Step-1: Run a mssql docker container locally  
```
docker run --name RESC_DB_LOCAL -e "ACCEPT_EULA=Y" -e "SA_PASSWORD=<enter a strong password>" -p 1433:1433 -d mcr.microsoft.com/mssql/server:2019-CU12-ubuntu-20.04
```

Step-2: Set following env variables.  
Windows:
```
SET MSSQL_DB_HOST=localhost
SET MSSQL_DB_PORT=1433
SET MSSQL_SCHEMA=master
SET MSSQL_USERNAME=sa
SET MSSQL_PASSWORD=<password>
SET MSSQL_ODBC_DRIVER=SQL Server
```

Mac:  
```
export MSSQL_DB_HOST=localhost
export MSSQL_DB_PORT=1433
export MSSQL_SCHEMA=master
export MSSQL_USERNAME=sa
export MSSQL_PASSWORD=<password>
export MSSQL_ODBC_DRIVER="ODBC Driver 17 for SQL Server"
```  

Step-3: Run migration script for latest revison to keep your local DB up to date.
```
alembic upgrade <last_revision_identifier>
```

Step-4: Generate revision for any change.  
```
alembic revision --autogenerate -m "<comment>"
```

To connect and view the tables from Intellij IDEA Ultimate edition refer the steps mentioned here.
https://www.jetbrains.com/help/idea/db-tutorial-connecting-to-ms-sql-server.html#connect-by-using-sql-server-authentication  

####Known issue:  
While auto generating revision script, Alembic is now including the changes for default master schema.
This needs to be fixed by creating a new schema called resc, then connecting to resc and run the revision script.


## References
[Alembic documentation](https://alembic.sqlalchemy.org/en/latest/index.html)
How to create a connection string: https://docs.sqlalchemy.org/en/14/core/engines.html