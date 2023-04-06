import logging
from typing import Any

import eave.stdlib.api_util
from fastapi import FastAPI, Request

from .public.requests.oauth_handlers import google_oauth, slack_oauth

from .internal.config import app_config
from .public.requests import access_requests, documents, subscriptions, slack_sources
from .public.requests import util as eave_request_util

if app_config.monitoring_enabled:
    import google.cloud.logging

    client = google.cloud.logging.Client()
    client.setup_logging()

    logging.info("Google Cloud Logging started for eave-api-core")

app = FastAPI()

eave.stdlib.api_util.add_standard_endpoints(app=app)
eave_request_util.add_standard_exception_handlers(app=app)

# @app.middleware("http")
# async def log_body(request: Request, call_next: Any):
#     body = await request.body()
#     print(body)
#     response = await call_next(request)
#     return response

app.post("/access_request")(access_requests.create_access_request)
app.post("/documents/upsert")(documents.upsert_document)
app.post("/subscriptions/create")(subscriptions.create_subscription)
app.post("/subscriptions/query")(subscriptions.get_subscription)
app.get("/oauth/google/authorize")(google_oauth.google_oauth_authorize)
app.get("/oauth/google/callback")(google_oauth.google_oauth_callback)
app.get("/oauth/slack/authorize")(slack_oauth.slack_oauth_authorize)
app.get("/oauth/slack/callback")(slack_oauth.slack_oauth_callback)
app.post("/slack_sources/query")(slack_sources.query)