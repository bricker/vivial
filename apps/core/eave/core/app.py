import logging
from typing import Any

import eave.stdlib.api_util
from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError

from .internal.config import app_config
from .public.requests import access_requests, documents, google_oauth, subscriptions
from .public.requests import util as eave_request_util

if app_config.monitoring_enabled:
    import google.cloud.logging

    client = google.cloud.logging.Client()
    client.setup_logging()

    logging.info("Google Cloud Logging started for eave-api-core")

# logging.basicConfig(level=logging.DEBUG)

app = FastAPI()

eave.stdlib.api_util.add_standard_endpoints(app=app)
eave_request_util.add_standard_exception_handlers(app=app)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
    print(exc_str)
    print(exc.body)
    return Response(status_code=422)


app.post("/access_request")(access_requests.create_access_request)
app.post("/documents/upsert")(documents.upsert_document)
app.post("/subscriptions/create")(subscriptions.create_subscription)
app.post("/subscriptions/query")(subscriptions.get_subscription)
app.get("/oauth/google/authorize")(google_oauth.google_oauth_authorize)
app.get("/oauth/google/callback")(google_oauth.google_oauth_callback)
