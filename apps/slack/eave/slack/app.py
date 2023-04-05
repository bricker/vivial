from typing import Any

import eave.stdlib.api_util as eave_api_util
import eave.stdlib.logging
from fastapi import FastAPI, Request

from . import slack_app

eave.stdlib.logging.setup_logging()

api = FastAPI()

eave_api_util.add_standard_endpoints(app=api, path_prefix="/slack")

@api.post("/slack/events")
async def slack_event(req: Request) -> Any:
    return await slack_app.handler.handle(req)
