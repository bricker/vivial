import logging
import sys

from fastapi import FastAPI, Request
from pydantic import BaseModel
import eave.core_api
import eave.openai

import eave.event_handlers
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
async def slack_event(req: Request) -> None:
    await eave.slack.handler.handle(req)

# class GenerateInput(BaseModel):
#     subscription_id: str
#     algorithm: ContextAlgorithm
#     prompt_prefix: str
#     prompt_suffix: str
#     openai_params: eave.openai.CompletionParameters

# @api.post("/_generate")
# async def generator(input: GenerateInput) -> str|None:
#     source = eave.core_api.SubscriptionSource(
#         id=input.subscription_id,
#         event=eave.core_api.SubscriptionSourceEvent.slack_message
#     )

#     source_details = source.details
#     msg = await eave.slack.client.conversations_history(
#         channel=source_details.channel,
#         oldest=source_details.ts,
#         inclusive=True,
#         limit=1
#     )

#     msgs_json = msg.get("messages")
#     assert msgs_json is not None
#     message = SlackMessage(msgs_json[0], channel=source_details.channel)

#     match input.algorithm:
#         case ContextAlgorithm.mapreduce:
#             context = await MapReduceAlgorithm.build_context(message=message)
#         case ContextAlgorithm.concat:
#             context = await SimpleConcatenationAlgorithm.build_context(message=message)
#         case ContextAlgorithm.rolling:
#             context = await RollingContextAlgorithm.build_context(message=message)

#     full_prompt = (
#         f"{input.prompt_prefix}"
#         f"\n\n###\n\n"
#         f"Context:\n"
#         f"{context}"
#         f"{input.prompt_suffix}"
#     )

#     params = input.openai_params
#     params.prompt = full_prompt
#     answer = await eave.openai.summarize(params)
#     return answer

@api.get("/status")
@api.get("/_ah/start")
@api.get("/_ah/warmup")
@api.get("/_ah/stop")
def health() -> dict[str, str]:
    return {"status": "1"}
