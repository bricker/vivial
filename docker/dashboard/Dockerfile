# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.12
ARG NODE_VERSION=18

## Python Builder
FROM python:${PYTHON_VERSION}-slim as builder-py
ENV EAVE_HOME=/build
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y git

# Copy the full monorepo into the builder image
RUN mkdir -p ${EAVE_HOME}
COPY . ${EAVE_HOME}/

# Install dependencies
RUN mkdir -p /vendor
RUN python -m pip install \
    -t /vendor \
    -r ${EAVE_HOME}/apps/core/requirements.txt \
    -r ${EAVE_HOME}/apps/core/requirements-vendor.txt


## Node Builder
FROM node:${NODE_VERSION}-slim as builder-node
ENV EAVE_HOME=/build
ENV NODE_ENV=development

RUN apt-get update && apt-get install -y git

# Copy the full monorepo into the builder image
RUN mkdir -p ${EAVE_HOME}
COPY . ${EAVE_HOME}/

WORKDIR ${EAVE_HOME}/apps/dashboard

# Install dependencies
RUN npm ci --force
RUN npx webpack build --mode=production --no-devtool

## Base
FROM python:${PYTHON_VERSION}-slim as base

# Copy dependencies into base image
RUN mkdir -p /vendor
COPY --from=builder-py /vendor /vendor/

# Copy only the app source code into the Docker image.
# This excludes things like migration scripts, development scripts, tests, and requirements files.
# This also excludes the rest of the monorepo.
RUN mkdir -p /app/eave
COPY --from=builder-node /build/apps/dashboard/eave /app/eave/

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

USER appuser

WORKDIR /app
EXPOSE 8000

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

CMD PYTHONPATH=/vendor python -m gunicorn \
    --bind :8000 \
    --pythonpath /vendor \
    --workers 3 \
    eave.dashboard.app:app
