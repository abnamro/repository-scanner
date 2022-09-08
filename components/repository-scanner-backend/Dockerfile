FROM python:3.9.13-alpine3.16

ARG NAME="repository_scanner_backend"
ARG DESCRIPTION="Repository Scanner backend"
ARG VERSION=${VERSION}
ARG RUN_AS_USER="apiuser"

# hadolint ignore=DL3018
RUN apk add --no-cache nginx build-base linux-headers pcre-dev

# Adding dev dependencies for pyjwt
# hadolint ignore=DL3018
RUN apk add --no-cache --virtual .build-deps pcre-dev gcc musl-dev python3-dev libffi-dev openssl-dev

# hadolint ignore=DL3017
RUN apk upgrade -U -a

# hadolint ignore=DL3018
RUN apk add --no-cache git

# Install MSSQL ODBC Drivers
RUN apk add curl
#Download the MSSQL ODBC Driver package(s)
RUN curl -O https://download.microsoft.com/download/e/4/e/e4e67866-dffd-428c-aac7-8d28ddafb39b/msodbcsql17_17.8.1.1-1_amd64.apk
RUN curl -O https://download.microsoft.com/download/e/4/e/e4e67866-dffd-428c-aac7-8d28ddafb39b/mssql-tools_17.8.1.1-1_amd64.apk

#Verify MSSQL ODBC Driver signature:
RUN curl -O https://download.microsoft.com/download/e/4/e/e4e67866-dffd-428c-aac7-8d28ddafb39b/msodbcsql17_17.8.1.1-1_amd64.sig
RUN curl -O https://download.microsoft.com/download/e/4/e/e4e67866-dffd-428c-aac7-8d28ddafb39b/mssql-tools_17.8.1.1-1_amd64.sig

RUN apk add gnupg
RUN curl https://packages.microsoft.com/keys/microsoft.asc  | gpg --import -
RUN gpg --verify msodbcsql17_17.8.1.1-1_amd64.sig msodbcsql17_17.8.1.1-1_amd64.apk
RUN gpg --verify mssql-tools_17.8.1.1-1_amd64.sig mssql-tools_17.8.1.1-1_amd64.apk
# hadolint ignore=DL3018
RUN apk --purge del gnupg

#Install the MSSQL ODBC Driver package(s)
RUN apk add --allow-untrusted msodbcsql17_17.8.1.1-1_amd64.apk
RUN apk add --allow-untrusted mssql-tools_17.8.1.1-1_amd64.apk

# Install MSSQL Python Driver dependencies
RUN apk add g++ unixodbc-dev

RUN mkdir /repository_scanner_backend

COPY ./ /repository_scanner_backend
RUN addgroup -S $RUN_AS_USER && adduser -S $RUN_AS_USER -g "$RUN_AS_USER"
RUN chown -R $RUN_AS_USER:$RUN_AS_USER ./repository_scanner_backend

USER $RUN_AS_USER
ENV PATH=$PATH:/home/apiuser/.local/bin
# hadolint ignore=DL3013
RUN pip install -U pip
# hadolint ignore=DL3013
RUN pip install pyodbc==4.0.32
# hadolint ignore=DL3013
RUN pip install -e /repository_scanner_backend

# Remove pyjwt dependencies, needs root
USER root
# hadolint ignore=DL3018
RUN apk --purge del .build-deps

USER $RUN_AS_USER

WORKDIR /repository_scanner_backend
