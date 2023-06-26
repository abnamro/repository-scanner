#!/bin/bash
################################################################################################
#Script Name	: run_newman_tests.sh
#Description	: This script runs newman tests for RESC API
#Args         : -b <resc-backend image:tag> -d <resc-database image:tag>  -n <newman image:tag>
#Usage 1      : ./run_newman_tests.sh -b 'rescabnamro/resc-backend:latest'  \
#                -d 'mcr.microsoft.com/azure-sql-edge:1.0.5'  \
#                -n "postman/newman:5.3.1-alpine"
#Usage 2      : ./run_newman_tests.sh , default values will be used
#                if you don't provide any argument
#Author       : Repository Scanner
#Email        : resc@nl.abnamro.com
################################################################################################
echo "*** Checking python installation ***"

python_installation=$(which python3)

echo "*** Installing pyntcli ***"
$python_installation -m pip install pyntcli

echo "*** Setting up the test environment ***"

# Fetch arguments provided to script
while getopts b:d:n: flag
do
    case "${flag}" in
        b) backend_image=${OPTARG};;
        d) database_image=${OPTARG};;
        n) newman_image=${OPTARG};;
    esac
done

RESC_BACKEND_IMAGE="${backend_image:-"rescabnamro/resc-backend:latest"}"
RESC_DATABASE_IMAGE="${database_image:-"mcr.microsoft.com/azure-sql-edge:1.0.5"}"
RESC_NEWMAN_IMAGE="${newman_image:-"postman/newman:5.3.1-alpine"}"
RESC_BACKEND_CONTAINER="resc-api-test"
RESC_DATABASE_CONTAINER="resc-database-test"
RESC_NEWMAN_CONTAINER="resc-newman-test"
RESC_API_PORT=8001
MSSQL_ODBC_DRIVER="ODBC Driver 18 for SQL Server"

# Print image versions to be used for testing
echo "RESC Backend Image: $RESC_BACKEND_IMAGE";
echo "RESC Database Image: $RESC_DATABASE_IMAGE";
echo "RESC Newman Image: $RESC_NEWMAN_IMAGE";

## Initial clean up
echo "*** Initial Clean Up: Removing Containers If Already Running ***"
docker rm -f $RESC_BACKEND_CONTAINER || true
docker rm -f $RESC_DATABASE_CONTAINER || true
docker rm -f $RESC_NEWMAN_CONTAINER || true

# Loading environment variables
echo "*** Loading Environment Variables ***"
set -o allexport;source test.env;set +o allexport

# Generate password for RESC Database
echo "*** Generating Random Password For RESC Database ***"
# shellcheck disable=SC2002
RESC_DATABASE_PASSWORD=$(date +%s | sha256sum | base64 | head -c 50)
if [[ -z $RESC_DATABASE_PASSWORD ]]
then
  echo "ERROR: Unable to generate password for RESC Database"
  exit 1
fi

# Running RESC Database container
echo "*** Running $RESC_DATABASE_CONTAINER Container ***"
docker run -d --cap-add SYS_PTRACE -e 'ACCEPT_EULA=1' -e MSSQL_SA_PASSWORD="$RESC_DATABASE_PASSWORD" \
-p "$MSSQL_DB_PORT":"$MSSQL_DB_PORT" --name $RESC_DATABASE_CONTAINER "$RESC_DATABASE_IMAGE"

# Retrieve RESC Database container IP address
sleep 25
RESC_DATABASE_HOST_IP=$(docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $RESC_DATABASE_CONTAINER)
echo "*** IP Address Of $RESC_DATABASE_CONTAINER Container is: $RESC_DATABASE_HOST_IP ***"

# Running RESC API container
echo "*** Running $RESC_BACKEND_CONTAINER Container ***"
docker run -d --env-file test.env -e MSSQL_ODBC_DRIVER="$MSSQL_ODBC_DRIVER" -e MSSQL_DB_HOST="$RESC_DATABASE_HOST_IP" \
-e MSSQL_PASSWORD="$RESC_DATABASE_PASSWORD" --name $RESC_BACKEND_CONTAINER -p $RESC_API_PORT:$RESC_API_PORT "$RESC_BACKEND_IMAGE" \
/bin/sh -c "alembic upgrade head && uvicorn resc_backend.resc_web_service.api:app --workers 1 --host 0.0.0.0 --port $RESC_API_PORT"

sleep 15
echo "*** Printing Logs Of $RESC_BACKEND_CONTAINER Container ***"
docker logs $RESC_BACKEND_CONTAINER

# Retrieve RESC API container IP address
RESC_API_HOST_IP=$(docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $RESC_BACKEND_CONTAINER)
echo "*** IP Address Of $RESC_BACKEND_CONTAINER Container is: $RESC_API_HOST_IP ***"

# Clean up
function cleanUp() {
  echo "*** Running Clean Up: Stopping Containers ***"
  docker stop $RESC_NEWMAN_CONTAINER || true
  docker stop $RESC_BACKEND_CONTAINER || true
  docker stop $RESC_DATABASE_CONTAINER || true
  echo "*** Running Clean Up: Removing Containers ***"
  docker rm -f $RESC_NEWMAN_CONTAINER || true
  docker rm -f $RESC_BACKEND_CONTAINER || true
  docker rm -f $RESC_DATABASE_CONTAINER || true
  echo "*** Running Clean Up: Removing test artifacts ***"
  rm -f $PWD/gitleaks.toml
}

# Running Newman Tests
echo "*** Downloading latest gitleaks.toml rule file ***"
curl https://raw.githubusercontent.com/zricethezav/gitleaks/master/config/gitleaks.toml > gitleaks.toml

# Stops on Newman test failure
set -e;

function onExit {
    if [ "$?" != "0" ]; then
        echo "Newman Tests failed";
        cleanUp
        exit 1;
    else
        echo "Newman Tests passed";
        cleanUp
    fi
}
trap onExit EXIT;

echo "*** Generating environment file ***"
echo "{\"id\": \"bb6154d5-15d4-4c83-ab65-639feb4198c1\",\"name\": \"resc-functional-test-env\",\"values\": [{\"key\": \"baseUrl\",\"value\": \"http://${RESC_API_HOST_IP}:${RESC_API_PORT}\",\"type\": \"default\",\"enabled\": true}],\"_postman_variable_scope\": \"environment\",\"_postman_exported_at\": \"2023-06-21T14:42:58.583Z\",\"_postman_exported_using\": \"Postman/10.15.1\"}" > resc-functional-test-env.json
echo "*** Setup test environment ***"

echo "*** Running Newman Tests ***"

pynt newman --collection ./RESC_web_service.postman_collection.json --environment ./resc-functional-test-env.json
echo "*** Done ***"





