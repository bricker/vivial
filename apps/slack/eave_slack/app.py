import logging
import sys
from typing import Any

from fastapi import FastAPI, Request

import eave_stdlib.api_util as eave_api_util
from . import slack_app
from .config import app_config

if app_config.monitoring_enabled:
    # TODO: Move this into eave_stdlib
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

eave_api_util.RouterInterface.register(FastAPI)
eave_api_util.add_standard_endpoints(app=api, path_prefix="/slack")

@api.post("/slack/events")
async def slack_event(req: Request) -> Any:
    handler = await slack_app.get_slack_app_handler()
    return await handler.handle(req)
