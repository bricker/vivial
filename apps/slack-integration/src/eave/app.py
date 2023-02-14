import logging
import sys

from fastapi import FastAPI, Request

import eave.event_handlers
import eave.slack_app as slack
from eave.settings import APP_SETTINGS

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
async def endpoint(req: Request) -> None:
    await slack.handler.handle(req)


@api.get("/status")
@api.get("/_ah/start")
@api.get("/_ah/warmup")
@api.get("/_ah/stop")
def health() -> dict[str, str]:
    return {"status": "1"}


slack.app.event("message")(eave.event_handlers.MessageEventHandler().handler)
slack.app.shortcut("eave_watch_request")(eave.event_handlers.WatchRequestEventHandler().handler)
