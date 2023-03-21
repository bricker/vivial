import logging
from typing import Optional

from slack_sdk.errors import SlackApiError
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.web.async_slack_response import AsyncSlackResponse

from .config import shared_config

_eave_slack_client: Optional[AsyncWebClient] = None

async def eave_slack_client() -> AsyncWebClient:
    global _eave_slack_client

    if _eave_slack_client is None:
        token = await shared_config.eave_slack_system_bot_token
        _eave_slack_client = AsyncWebClient(token=token)

    return _eave_slack_client
