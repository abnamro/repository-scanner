FROM python:3.9.13-alpine3.16

ARG NAME="resc vcs scanner"
ARG DESCRIPTION=" RESC Version Control System Scanner"
ARG VERSION=${VERSION}
ARG RUN_AS_USER="apiuser"

# hadolint ignore=DL3018
RUN apk add --no-cache --virtual .build-deps gcc g++ pcre-dev musl-dev python3-dev libffi-dev openssl-dev

# hadolint ignore=DL3017
RUN apk upgrade -U -a

# hadolint ignore=DL3018
RUN apk add --no-cache git

RUN mkdir /resc_backend

COPY ./resc-backend /resc_backend
RUN addgroup -S $RUN_AS_USER && adduser -S $RUN_AS_USER -g "$RUN_AS_USER"
RUN chown -R $RUN_AS_USER:$RUN_AS_USER ./resc_backend

RUN mkdir /vcs_scanner

COPY ./resc-vcs-scanner /vcs_scanner
RUN chown -R $RUN_AS_USER:$RUN_AS_USER ./vcs_scanner
RUN chmod +x ./vcs_scanner/gitleaks_config/seco-gitleaks-linux-amd64

USER $RUN_AS_USER
ENV PATH=$PATH:/home/apiuser/.local/bin
# hadolint ignore=DL3013
RUN pip install -U pip

RUN pip install -e /resc_backend

# hadolint ignore=DL3013
RUN pip install -e /vcs_scanner

# Remove build dependencies, needs root
USER root
# hadolint ignore=DL3018
RUN apk --purge del .build-deps

USER $RUN_AS_USER

WORKDIR /vcs_scanner
