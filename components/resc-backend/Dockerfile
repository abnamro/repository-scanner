FROM python:3.9.16-alpine3.17

ARG NAME="resc_backend"
ARG DESCRIPTION="Repository Scanner Backend"
ARG VERSION=${VERSION}
ARG RUN_AS_USER="apiuser"
ARG RUN_AS_GROUP="apiuser"
ARG UID=10001
ARG GID=10002

RUN apk -U upgrade \
&& apk add --no-cache curl git nginx build-base linux-headers \
&& apk add --no-cache --virtual .build-deps pcre-dev gcc musl-dev python3-dev libffi-dev openssl-dev \
&& curl -O https://download.microsoft.com/download/8/6/8/868e5fc4-7bfe-494d-8f9d-115cbcdb52ae/msodbcsql18_18.1.2.1-1_amd64.apk \
&& curl -O https://download.microsoft.com/download/8/6/8/868e5fc4-7bfe-494d-8f9d-115cbcdb52ae/mssql-tools18_18.1.1.1-1_amd64.apk \
&& curl -O https://download.microsoft.com/download/8/6/8/868e5fc4-7bfe-494d-8f9d-115cbcdb52ae/msodbcsql18_18.1.2.1-1_amd64.sig \
&& curl -O https://download.microsoft.com/download/8/6/8/868e5fc4-7bfe-494d-8f9d-115cbcdb52ae/mssql-tools18_18.1.1.1-1_amd64.sig \
&& apk add gnupg \
&& curl https://packages.microsoft.com/keys/microsoft.asc  | gpg --import - \
&& gpg --verify msodbcsql18_18.1.2.1-1_amd64.sig msodbcsql18_18.1.2.1-1_amd64.apk \
&& gpg --verify mssql-tools18_18.1.1.1-1_amd64.sig mssql-tools18_18.1.1.1-1_amd64.apk \
&& apk add --allow-untrusted msodbcsql18_18.1.2.1-1_amd64.apk \
&& apk add --allow-untrusted mssql-tools18_18.1.1.1-1_amd64.apk \
&& apk add g++ unixodbc-dev

RUN mkdir /resc_backend

COPY ./ /resc_backend

RUN addgroup -g $GID $RUN_AS_GROUP \
&& adduser -D -u $UID -G $RUN_AS_GROUP $RUN_AS_USER \
&& chown -R $RUN_AS_USER:$RUN_AS_GROUP ./resc_backend

USER $RUN_AS_USER
ENV PATH=$PATH:/home/apiuser/.local/bin

RUN pip install --no-cache-dir --upgrade pyodbc==4.0.32 -e /resc_backend

USER root

RUN apk --purge del gnupg .build-deps

USER $RUN_AS_USER

WORKDIR /resc_backend
