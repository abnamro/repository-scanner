FROM python:3.9.16-alpine3.17

ARG NAME="resc-vcs-scraper"
ARG DESCRIPTION="Version Control Systems Scraper"
ARG VERSION=${VERSION}
ARG RUN_AS_USER="apiuser"
ARG RUN_AS_GROUP="apiuser"
ARG UID=10001
ARG GID=10002

RUN apk -U upgrade \
&& apk add --no-cache --virtual .build-deps pcre-dev gcc musl-dev python3-dev libffi-dev openssl-dev \
&& mkdir /vcs-scraper

COPY ./ /vcs-scraper

RUN addgroup -g $GID $RUN_AS_GROUP \
&& adduser -D -u $UID -G $RUN_AS_GROUP $RUN_AS_USER \
&& chown -R $RUN_AS_USER:$RUN_AS_GROUP ./vcs-scraper

USER $RUN_AS_USER

ENV PATH=$PATH:/home/apiuser/.local/bin

RUN pip install --no-cache-dir --upgrade /vcs-scraper

USER root

RUN apk --purge del gnupg .build-deps

USER $RUN_AS_USER

WORKDIR /vcs-scraper
