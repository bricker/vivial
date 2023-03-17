import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from eave_core.public.requests import (
    create_access_request,
    create_subscription,
    get_subscription,
    google_oauth,
    upsert_document,
)
from eave_core.internal.middleware import TeamLookupMiddleware
from eave_core.internal.config import app_config
import eave_stdlib.util

if app_config.monitoring_enabled:
    import google.cloud.logging

    client = google.cloud.logging.Client()
    client.setup_logging()

    logging.info("Google Cloud Logging started for eave-api-core")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(TeamLookupMiddleware)

@app.get("/status")
def status() -> eave_stdlib.util.JsonObject:
    return {
        "service": "api",
        "status": "OK",
        "version": app_config.app_version,
    }


app.post("/access_request")(create_access_request.CreateAccessRequest.handler)

# TODO: These need auth
app.post("/documents/upsert")(upsert_document.UpsertDocument.handler)
app.post("/subscriptions/create")(create_subscription.CreateSubscription.handler)
app.post("/subscriptions/query")(get_subscription.GetSubscription.handler)

app.get("/oauth/google/authorize")(google_oauth.GoogleOauthInit.handler)
app.get("/oauth/google/callback")(google_oauth.GoogleOauthCallback.handler)
