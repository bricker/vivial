from slack_sdk.web.async_client import AsyncWebClient

from .config import shared_config

token = shared_config.eave_slack_system_bot_token
eave_slack_client = AsyncWebClient(token=token)
