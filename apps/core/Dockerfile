# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.12

FROM python:${PYTHON_VERSION}-slim as builder
ENV EAVE_HOME=/build
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN mkdir -p /build/apps/core
COPY apps/core /build/apps/core

RUN mkdir -p /build/libs/eave-pubsub-schemas
COPY libs/eave-pubsub-schemas /build/libs/eave-pubsub-schemas

RUN mkdir -p /build/libs/eave-stdlib-py
COPY libs/eave-stdlib-py /build/libs/eave-stdlib-py

RUN apt-get update && apt-get install -y git

RUN mkdir -p /build/vendor
RUN python -m pip install \
    -t /build/vendor \
    -r /build/apps/core/requirements.txt \
    -r /build/apps/core/requirements-vendor.txt


FROM python:${PYTHON_VERSION}-slim as base
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/vendor

RUN mkdir -p /vendor
COPY --from=builder /build/vendor /vendor

RUN mkdir -p /app/eave
COPY --from=builder /build/apps/core/eave /app/eave

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

CMD python -m gunicorn \
    --bind :8000 \
    --pythonpath /vendor \
    --workers 3 \
    --worker-class uvicorn.workers.UvicornWorker \
    eave.core.app:app
