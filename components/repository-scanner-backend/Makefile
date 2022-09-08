SHELL:=/bin/bash

sts_port = 1234

test:
	@pip install tox
	tox

db: cleandb create_db env init_db

env:
	@pip install virtualenv
	@if ! test -f "venv"; then python -m virtualenv venv ;fi
	@export PIP_CONFIG_FILE="./pip.conf" && pip install -e .
	@pip install pyodbc==4.0.32

create_db:
	@docker pull mcr.microsoft.com/mssql/server:2019-CU12-ubuntu-20.04
	source db.env && docker run --name resc-db -e "ACCEPT_EULA=Y" -e "SA_PASSWORD=$$MSSQL_PASSWORD" -e "MSSQL_PID=Express"  -p $$MSSQL_DB_PORT:$$MSSQL_DB_PORT -d mcr.microsoft.com/mssql/server:2019-CU12-ubuntu-20.04

init_db:
	@echo "waiting for database to be ready"
	@source db.env && while ! docker exec resc-db /opt/mssql-tools/bin/sqlcmd -S $$MSSQL_DB_HOST -U $$MSSQL_USERNAME -P $$MSSQL_PASSWORD; do sleep 1;done
	@source db.env && docker exec resc-db /opt/mssql-tools/bin/sqlcmd -S $$MSSQL_DB_HOST -U $$MSSQL_USERNAME -P $$MSSQL_PASSWORD -q "create database $$MSSQL_SCHEMA"
	@source venv/bin/activate && source db.env && alembic upgrade head
	@docker cp $$PWD/test_data/database_dummy_data.sql resc-db:/tmp
	@source db.env && docker exec resc-db /opt/mssql-tools/bin/sqlcmd -S $$MSSQL_DB_HOST -d $$MSSQL_SCHEMA -U $$MSSQL_USERNAME -P $$MSSQL_PASSWORD -i "/tmp/database_dummy_data.sql"

cleandb:
	@docker rm resc-db --force

sts:
	@source venv/bin/activate && source db.env && uvicorn repository_scanner_backend.resc_web_service.api:app --workers 1 --host $$MSSQL_DB_HOST --port $(sts_port) --reload

clean:
	@rm -rf venv
	@find . -type f -name '*.pyc' -delete
	@find . -type d -name '__pycache__' | xargs rm -rf
	@find . -type d -name '*.ropeproject' | xargs rm -rf
	@rm -rf build/
	@rm -rf dist/
	@rm -rf src/*.egg*
	@rm -f MANIFEST
	@rm -rf docs/build/
	@rm -f .coverage.*
	@rm -rf .tox/
