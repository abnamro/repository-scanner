#!/bin/bash
################################################################################################
#Script Name	: run_zap_api_tests.sh
#Description	: This script runs ZAP API Security tests for RESC API
#Args         : -b <resc-backend image:tag> -d <resc-database image:tag>  -z <zap image:tag>
#Usage 1      : ./run_zap_api_tests.sh -b 'rescabnamro/resc-backend:latest'  \
#                -d 'mcr.microsoft.com/azure-sql-edge:1.0.7'  \
#                   -z "owasp/zap2docker-weekly"
#Usage 2      : ./run_zap_api_tests.sh , default values will be used
#                if you don't provide any argument
#Author       : Repository Scanner
#Email        : resc@nl.abnamro.com
################################################################################################
echo "*** Running ZAP API Security Tests ***"

# Fetch arguments provided to script
while getopts b:d: flag
do
    case "${flag}" in
        b) backend_image=${OPTARG};;
        d) database_image=${OPTARG};;
        z) zap_image=${OPTARG};;
    esac
done

RESC_BACKEND_IMAGE="${backend_image:-"rescabnamro/resc-backend:latest"}"
RESC_DATABASE_IMAGE="${database_image:-"mcr.microsoft.com/azure-sql-edge:1.0.7"}"
RESC_ZAP_IMAGE="${zap_image:-"owasp/zap2docker-weekly"}"
RESC_BACKEND_CONTAINER="resc-api-test"
RESC_DATABASE_CONTAINER="resc-database-test"
RESC_ZAP_CONTAINER="resc-zap-test"
RESC_API_PORT=8001
MSSQL_ODBC_DRIVER="ODBC Driver 18 for SQL Server"

# Print image versions to be used for testing
echo "RESC Backend Image: $RESC_BACKEND_IMAGE";
echo "RESC Database Image: $RESC_DATABASE_IMAGE";

## Initial clean up
echo "*** Initial Clean Up: Removing Containers If Already Running ***"
docker rm -f $RESC_BACKEND_CONTAINER || true
docker rm -f $RESC_DATABASE_CONTAINER || true
docker rm -f $RESC_ZAP_CONTAINER || true

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

if [[ -z $RESC_DATABASE_HOST_IP ]]
then
  echo "ERROR: Unable to run RESC Database"
  exit 1
fi

# Running RESC API container
echo "*** Running $RESC_BACKEND_CONTAINER Container ***"
docker run -d --env-file test.env -e MSSQL_ODBC_DRIVER="$MSSQL_ODBC_DRIVER" -e MSSQL_DB_HOST="$RESC_DATABASE_HOST_IP" \
-e MSSQL_PASSWORD="$RESC_DATABASE_PASSWORD" --name $RESC_BACKEND_CONTAINER -p $RESC_API_PORT:$RESC_API_PORT "$RESC_BACKEND_IMAGE" \
/bin/sh -c "alembic upgrade head && python ./test_data/insert_test_data.py && uvicorn resc_backend.resc_web_service.api:app --workers 1 --host 0.0.0.0 --port $RESC_API_PORT"

sleep 15
echo "*** Printing Logs Of $RESC_BACKEND_CONTAINER Container ***"
docker logs $RESC_BACKEND_CONTAINER

# Retrieve RESC API container IP address
RESC_API_HOST_IP=$(docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $RESC_BACKEND_CONTAINER)
echo "*** IP Address Of $RESC_BACKEND_CONTAINER Container is: $RESC_API_HOST_IP ***"

if [[ -z $RESC_API_HOST_IP ]]
then
  echo "ERROR: Unable to run RESC API"
  exit 1
fi

# Clean up
function cleanUp() {
  echo "*** Running Clean Up: Stopping Containers ***"
  docker stop $RESC_ZAP_CONTAINER || true
  docker stop $RESC_BACKEND_CONTAINER || true
  docker stop $RESC_DATABASE_CONTAINER || true
  echo "*** Running Clean Up: Removing Containers ***"
  docker rm -f $RESC_ZAP_CONTAINER || true
  docker rm -f $RESC_BACKEND_CONTAINER || true
  docker rm -f $RESC_DATABASE_CONTAINER || true
}

# Stops on ZAP API test failure
set -e;

function onExit {
    if [ "$?" != "0" ]; then
        echo "ZAP Tests failed";
        cleanUp
        exit 1;
    else
        echo "ZAP Tests passed";
        cleanUp
    fi
}
trap onExit EXIT;

# Running ZAP API Security Tests
echo "*** Running ZAP API Tests From $RESC_ZAP_CONTAINER Container ***"
echo "Running ZAP API Security Test Scan "
docker run -v $(pwd):/zap/wrk/:rw -t $RESC_ZAP_IMAGE zap-api-scan.py -t http://$RESC_API_HOST_IP:$RESC_API_PORT/openapi.json -f openapi -I

