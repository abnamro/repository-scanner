FROM python:3.9.9-alpine3.15

ARG NAME="resc/vcs-scraper"
ARG DESCRIPTION="Version Control Systems' scraper"
ARG VERSION=${VERSION}
ARG RUN_AS_USER="apiuser"

# hadolint ignore=DL3017
RUN apk upgrade -U -a

RUN mkdir /vcs-scraper

COPY ./ /vcs-scraper
RUN addgroup -S $RUN_AS_USER && adduser -S $RUN_AS_USER -g "$RUN_AS_USER"
RUN chown -R $RUN_AS_USER:$RUN_AS_USER ./vcs-scraper

USER $RUN_AS_USER
ENV PATH=$PATH:/home/apiuser/.local/bin
# hadolint ignore=DL3013
RUN pip install -U pip
# hadolint ignore=DL3013
RUN pip install /vcs-scraper

WORKDIR /vcs-scraper
