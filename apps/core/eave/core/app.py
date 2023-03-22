import logging

from fastapi import FastAPI

from .public.requests import (
    access_requests,
    documents,
    google_oauth,
    subscriptions,
)
from .public.requests import util as eave_request_util
from .internal.config import app_config
import eave.stdlib.api_util

if app_config.monitoring_enabled:
    import google.cloud.logging

    client = google.cloud.logging.Client()
    client.setup_logging()

    logging.info("Google Cloud Logging started for eave-api-core")

app = FastAPI()

eave.stdlib.api_util.add_standard_endpoints(app=app)
eave_request_util.add_standard_exception_handlers(app=app)

app.post("/access_request")(access_requests.create_access_request)
app.post("/documents/upsert")(documents.upsert_document)
app.post("/subscriptions/create")(subscriptions.create_subscription)
app.post("/subscriptions/query")(subscriptions.get_subscription)
app.get("/oauth/google/authorize")(google_oauth.google_oauth_authorize)
app.get("/oauth/google/callback")(google_oauth.google_oauth_callback)
