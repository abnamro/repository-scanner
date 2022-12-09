FROM python:3.9.16-alpine3.17

ARG NAME="resc_backend"
ARG DESCRIPTION="Repository Scanner Backend"
ARG VERSION=${VERSION}
ARG RUN_AS_USER="apiuser"

RUN apk -U upgrade \
&& apk add --no-cache curl git nginx build-base linux-headers \
&& apk add --no-cache --virtual .build-deps pcre-dev gcc musl-dev python3-dev libffi-dev openssl-dev \
&& curl -O https://download.microsoft.com/download/e/4/e/e4e67866-dffd-428c-aac7-8d28ddafb39b/msodbcsql17_17.8.1.1-1_amd64.apk \
&& curl -O https://download.microsoft.com/download/e/4/e/e4e67866-dffd-428c-aac7-8d28ddafb39b/mssql-tools_17.8.1.1-1_amd64.apk \
&& curl -O https://download.microsoft.com/download/e/4/e/e4e67866-dffd-428c-aac7-8d28ddafb39b/msodbcsql17_17.8.1.1-1_amd64.sig \
&& curl -O https://download.microsoft.com/download/e/4/e/e4e67866-dffd-428c-aac7-8d28ddafb39b/mssql-tools_17.8.1.1-1_amd64.sig \
&& apk add gnupg \
&& curl https://packages.microsoft.com/keys/microsoft.asc  | gpg --import - \
&& gpg --verify msodbcsql17_17.8.1.1-1_amd64.sig msodbcsql17_17.8.1.1-1_amd64.apk \
&& gpg --verify mssql-tools_17.8.1.1-1_amd64.sig mssql-tools_17.8.1.1-1_amd64.apk \
&& apk add --allow-untrusted msodbcsql17_17.8.1.1-1_amd64.apk \
&& apk add --allow-untrusted mssql-tools_17.8.1.1-1_amd64.apk \
&& apk add g++ unixodbc-dev

RUN mkdir /resc_backend

COPY ./ /resc_backend

RUN addgroup -S $RUN_AS_USER && adduser -S $RUN_AS_USER -g "$RUN_AS_USER" \
&& chown -R $RUN_AS_USER:$RUN_AS_USER ./resc_backend

USER $RUN_AS_USER
ENV PATH=$PATH:/home/apiuser/.local/bin

RUN pip install --no-cache-dir --upgrade pyodbc==4.0.32 -e /resc_backend

USER root

RUN apk --purge del gnupg .build-deps

USER $RUN_AS_USER

WORKDIR /resc_backend
