from eave.stdlib.typing import JsonObject
from slack_bolt.async_app import AsyncBoltContext

def log_context(context: AsyncBoltContext) -> JsonObject:
    return context