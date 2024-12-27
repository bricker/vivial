# syntax=docker/dockerfile:1
# check=error=true

ARG PYTHON_VERSION=3.12.3
ARG NODE_VERSION=18


## Python Builder
FROM python:${PYTHON_VERSION}-slim AS builder-py
ENV EAVE_HOME=/build
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y git

# Copy relevant files
RUN mkdir -p ${EAVE_HOME}
COPY apps/admin ${EAVE_HOME}/apps/admin
COPY libs ${EAVE_HOME}/libs

WORKDIR ${EAVE_HOME}/apps/admin

# Install dependencies
RUN mkdir -p /vendor
RUN python -m pip install \
    -t /vendor \
    -r requirements.txt \
    -r requirements-vendor.txt





## Node Builder
FROM node:${NODE_VERSION}-slim AS builder-node
ENV EAVE_HOME=/build
ENV NODE_ENV=development

RUN apt-get update && apt-get install -y git

# Copy relevant files
RUN mkdir -p ${EAVE_HOME}
COPY apps/admin ${EAVE_HOME}/apps/admin
COPY develop ${EAVE_HOME}/develop

WORKDIR ${EAVE_HOME}/develop/javascript
RUN npm ci

WORKDIR ${EAVE_HOME}/apps/admin
RUN npm ci
RUN npx webpack build --mode=production --no-devtool






## Base
FROM python:${PYTHON_VERSION}-slim AS base

ARG GAE_RELEASE_DATE="unknown"
ARG GAE_SERVICE="admin"
ARG GAE_VERSION="unknown"

# Copy python dependencies into base image
# Notably, node dependencies are _not_ required for this image. The webpack bundle contains everything necessary.
RUN mkdir -p /vendor
COPY --from=builder-py /vendor /vendor/

# Copy the app source code into the Docker image.
RUN mkdir -p /app/eave
COPY --from=builder-node /build/apps/admin/eave /app/eave/

# Create a non-privileged user that the app will run under.
# See https://docs.docker.com/go/dockerfile-user-best-practices/
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "10001" \
    appuser

USER 10001

WORKDIR /app
EXPOSE 8000

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/vendor

ENV GAE_RELEASE_DATE="$GAE_RELEASE_DATE"
ENV GAE_SERVICE="$GAE_SERVICE"
ENV GAE_VERSION="$GAE_VERSION"

ENTRYPOINT ["python", "-m", "gunicorn", "--pythonpath", "/vendor", "--worker-class", "eave.stdlib.uvicorn.EaveUvicornWorker", "eave.admin.app:app"]
