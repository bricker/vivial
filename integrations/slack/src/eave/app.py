import json
import logging
import os
import sys
from typing import Any

from fastapi import FastAPI, Request
from pydantic import BaseModel

import eave.core_api
import eave.event_handlers
from eave.util import JsonObject

eave.event_handlers.ensure_import()
import eave.openai
import eave.slack
from eave.settings import APP_SETTINGS
from eave.slack_models import SlackMessage

if APP_SETTINGS.monitoring_enabled:
    import google.cloud.logging

    client = google.cloud.logging.Client()
    client.setup_logging()

    logging.info("Google Cloud Logging started for eave-app-slack")
else:
    # TODO: A better way to direct logs to stdout in dev
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# https://github.com/slackapi/bolt-python/tree/main/examples/fastapi

api = FastAPI()


@api.post("/slack/events")
async def slack_event(req: Request) -> Any:
    return await eave.slack.handler.handle(req)

@api.get("/slack/status")
def status() -> JsonObject:
    return {
        "service": "slack",
        "status": "OK",
        "version": os.getenv("GAE_VERSION", "unknown"),
    }
