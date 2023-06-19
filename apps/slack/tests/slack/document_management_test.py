from eave.slack.slack_models import SlackMessage
import eave.stdlib.core_api.models.team
from eave.stdlib.logging import LogContext
from .base import BaseTestCase
from eave.slack.brain.document_management import DocumentManagementMixin
from slack_bolt.async_app import AsyncBoltContext
from eave.stdlib.config import shared_config
import unittest.mock

eave_app_id = shared_config.eave_slack_app_id


class DocumentManagementMixinTest(BaseTestCase):
    async def test_build_resources_eave_messages_ignored(self) -> None:
        eave_ctx = LogContext()
        # givent the slack message has a thread with many link resources
        # including some from the Eave app
        eave_team = eave.stdlib.core_api.models.team.Team(
            id=self.anyuuid(),
            name=self.anystring(),
            document_platform=eave.stdlib.core_api.models.team.DocumentPlatform.confluence,
        )
        slack_context = AsyncBoltContext()
        assert slack_context.client is not None
        slack_message = SlackMessage(
            data={
                "ts": "123",
                "channel": "channel",
                "text": "a resource <https://google.com>",
                "app_id": "not_eave",
            },
            slack_ctx=slack_context,
            eave_ctx=eave_ctx,
        )
        # according to slack api docs, conversations.replies also returns the
        # root message that started the thread, not just replies to it, so we repeat
        # the first message here
        thread_messages = {
            "messages": [
                {
                    "ts": "123",
                    "channel": "channel",
                    "text": "a resource <https://google.com>",
                    "app_id": "not_eave",
                },
                {
                    "ts": "123",
                    "channel": "channel",
                    "text": "another resource <https://www.eave.fyi>",
                    "app_id": "not_eave",
                },
                {
                    "ts": "123",
                    "channel": "channel",
                    "text": "evil resource not to be included <https://www.evae.iyf>",
                    "app_id": eave_app_id,
                },
            ]
        }
        slack_context.client.conversations_replies = unittest.mock.MagicMock(  # type:ignore
            return_value=self.mock_coroutine(thread_messages)
        )
        slack_context.client.chat_getPermalink = unittest.mock.MagicMock(  # type:ignore
            return_value=self.mock_coroutine({})
        )

        sut = DocumentManagementMixin(
            message=slack_message,
            eave_team=eave_team,
            slack_ctx=slack_context,
            eave_ctx=eave_ctx,
        )

        # when we build the resources list from the message
        result = await sut.build_resources()

        # then all links resources, except ones from the eave app, should be included
        assert "https://google.com" in result
        assert "https://www.eave.fyi" in result
        assert "https://www.evae.iyf" not in result
