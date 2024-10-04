# syntax=docker/dockerfile:1
# check=error=true

ARG PYTHON_VERSION=3.12.3





## Builder
FROM python:${PYTHON_VERSION}-slim AS builder
ENV EAVE_HOME=/build
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y git

# Copy relevant files
RUN mkdir -p ${EAVE_HOME}
COPY apps/core ${EAVE_HOME}/apps/core
COPY libs ${EAVE_HOME}/libs

WORKDIR ${EAVE_HOME}/apps/core

# Install dependencies
RUN mkdir -p /vendor
RUN python -m pip install \
    -t /vendor \
    -r requirements.txt \
    -r requirements-vendor.txt





## Base
FROM python:${PYTHON_VERSION}-slim AS base

ARG GAE_RELEASE_DATE="unknown"
ARG GAE_SERVICE="core-api"
ARG GAE_VERSION="unknown"

# Copy dependencies into base image
RUN mkdir -p /vendor
COPY --from=builder /vendor /vendor/

# Copy the app source code into the Docker image.
RUN mkdir -p /app/eave
COPY --from=builder /build/apps/core/eave /app/eave/

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

ENTRYPOINT ["python", "-m", "gunicorn", "--pythonpath", "/vendor", "--worker-class", "eave.stdlib.uvicorn.EaveUvicornWorker", "eave.core.app:app"]
