import logging

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

import eave.public.requests as _requests
from eave.internal.middleware import TeamLookupMiddleware
from eave.internal.settings import APP_SETTINGS

if APP_SETTINGS.monitoring_enabled:
    import google.cloud.logging

    client = google.cloud.logging.Client()
    client.setup_logging()

    logging.info("Google Cloud Logging started for eave-api-core")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://www.eave.fyi",
        "https://www.eave.dev:5000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(TeamLookupMiddleware)

app.get("/status")(_requests.GetStatus.handler)
app.get("/_ah/start")(_requests.GetStatus.handler)
app.get("/_ah/stop")(_requests.GetStatus.handler)
app.get("/_ah/warmup")(_requests.GetStatus.handler)
app.post("/access_request")(_requests.CreateAccessRequest.handler)

app.post("/documents/upsert")(_requests.UpsertDocument.handler)
app.post("/subscriptions/create")(_requests.CreateSubscription.handler)
app.post("/subscriptions/query")(_requests.GetSubscription.handler)
