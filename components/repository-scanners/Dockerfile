FROM python:3.9.13-alpine3.16

ARG NAME="repository_scanners secret scanner"
ARG DESCRIPTION="RESC Secret Scanner"
ARG VERSION=${VERSION}
ARG RUN_AS_USER="apiuser"

# hadolint ignore=DL3018
RUN apk add --no-cache --virtual .build-deps gcc g++

# hadolint ignore=DL3017
RUN apk upgrade -U -a

# hadolint ignore=DL3018
RUN apk add --no-cache git

RUN mkdir /repository_scanners

COPY ./ /repository_scanners
RUN addgroup -S $RUN_AS_USER && adduser -S $RUN_AS_USER -g "$RUN_AS_USER"
RUN chown -R $RUN_AS_USER:$RUN_AS_USER ./repository_scanners
RUN chmod +x ./repository_scanners/gitleaks_config/seco-gitleaks-linux-amd64

USER $RUN_AS_USER
ENV PATH=$PATH:/home/apiuser/.local/bin
# hadolint ignore=DL3013
RUN pip install -U pip
# hadolint ignore=DL3013
RUN pip install -e /repository_scanners

# Remove build dependencies, needs root
USER root
# hadolint ignore=DL3018
RUN apk --purge del .build-deps

USER $RUN_AS_USER

WORKDIR /repository_scanners
