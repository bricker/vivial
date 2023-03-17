import logging

from slack_sdk.errors import SlackApiError
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.web.async_slack_response import AsyncSlackResponse

class SlackClient:
    """
    Although you could use this for any Slack instance, it is meant to be used for Eave's internal company Slack,
    for things like system notifications. It's a quick way to send a message to a channel when something interesting happens.
    Customer-facing Eave Slack integrations should happen in the Eave Slack app.
    """

    slack_client: AsyncWebClient

    def __init__(self, api_token: str) -> None:
        self.slack_client = AsyncWebClient(token=api_token)

    async def notify_slack(self, channel_id: str, text: str) -> AsyncSlackResponse:
        try:
            response = await self.slack_client.chat_postMessage(
                channel=channel_id,
                text=text,
            )
            return response
        except SlackApiError as e:
            logging.exception(e)
            raise e
