FROM python:3.9.16-alpine3.17

ARG NAME="resc-vcs-scanner"
ARG DESCRIPTION="RESC Version Control System Scanner"
ARG VERSION=${VERSION}
ARG RUN_AS_USER="apiuser"
ARG RUN_AS_GROUP="apiuser"
ARG UID=10001
ARG GID=10002

RUN apk -U upgrade \
&& apk add --no-cache git \
&& apk add --no-cache --virtual .build-deps gcc g++ pcre-dev musl-dev python3-dev libffi-dev openssl-dev

RUN mkdir /resc_backend && mkdir /vcs_scanner

COPY ./resc-backend /resc_backend

RUN addgroup -g $GID $RUN_AS_GROUP \
&& adduser -D -u $UID -G $RUN_AS_GROUP $RUN_AS_USER \
&& chown -R $RUN_AS_USER:$RUN_AS_GROUP ./resc_backend

COPY ./resc-vcs-scanner /vcs_scanner

RUN chown -R $RUN_AS_USER:$RUN_AS_GROUP ./vcs_scanner \
&& chmod +x ./vcs_scanner/gitleaks_config/seco-gitleaks-linux-amd64

USER $RUN_AS_USER

ENV PATH=$PATH:/home/apiuser/.local/bin

RUN pip install --no-cache-dir --upgrade -e /resc_backend -e /vcs_scanner

USER root

RUN apk --purge del .build-deps

USER $RUN_AS_USER

WORKDIR /vcs_scanner
