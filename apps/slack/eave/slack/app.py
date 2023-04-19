from typing import Any

import eave.stdlib.api_util as eave_api_util
import eave.stdlib.logging
from fastapi import FastAPI, Request
from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler

from . import slack_app

eave.stdlib.logging.setup_logging()

api = FastAPI()

eave_api_util.add_standard_endpoints(app=api, path_prefix="/slack")


@api.post("/slack/events")
async def slack_event(req: Request) -> Any:
    handler = AsyncSlackRequestHandler(slack_app.app)
    return await handler.handle(req)
