import slack_sdk.web.async_client

from .config import shared_config

def get_authenticated_eave_system_slack_client() -> slack_sdk.web.async_client.AsyncWebClient:
    token = shared_config.eave_slack_system_bot_token
    return slack_sdk.web.async_client.AsyncWebClient(token=token)
