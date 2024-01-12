import slack_sdk.web.async_client

from .config import SHARED_CONFIG


def get_authenticated_eave_system_slack_client() -> slack_sdk.web.async_client.AsyncWebClient:
    token = SHARED_CONFIG.eave_slack_system_bot_token
    return slack_sdk.web.async_client.AsyncWebClient(token=token)
