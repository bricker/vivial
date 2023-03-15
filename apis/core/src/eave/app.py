import json
import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import eave.public.requests as _requests
from eave.internal.middleware import TeamLookupMiddleware
from eave.internal.settings import APP_SETTINGS
from eave.internal.util import JsonObject

if APP_SETTINGS.monitoring_enabled:
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
def status() -> JsonObject:
    return {
        "service": "api",
        "status": "OK",
        "version": os.getenv("GAE_VERSION", "unknown"),
    }


app.post("/access_request")(_requests.CreateAccessRequest.handler)

# TODO: These need auth
app.post("/documents/upsert")(_requests.UpsertDocument.handler)
app.post("/subscriptions/create")(_requests.CreateSubscription.handler)
app.post("/subscriptions/query")(_requests.GetSubscription.handler)

app.get("/oauth/google/authorize")(_requests.GoogleOauthInit.handler)
app.get("/oauth/google/callback")(_requests.GoogleOauthCallback.handler)
