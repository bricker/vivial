from eave.slack.slack_models import SlackMessage
import eave.stdlib.core_api.models.team
from eave.stdlib.logging import LogContext
from .base import BaseTestCase
from eave.slack.brain.document_management import DocumentManagementMixin
from slack_bolt.async_app import AsyncBoltContext
from eave.stdlib.config import SHARED_CONFIG
import unittest.mock


class DocumentManagementMixinTest(BaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

        self.patch_env({"EAVE_SLACK_APP_ID": self.anystr("EAVE_SLACK_APP_ID")})

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
                "ts": self.anystr("slack ts 1"),
                "channel": self.anystr("slack channel"),
                "text": f"<{self.anyurl('url1')}>",
                "app_id": self.anystr("not eave app_id"),
            },
            slack_ctx=slack_context,
            eave_ctx=eave_ctx,
        )
        # according to slack api docs, conversations.replies also returns the
        # root message that started the thread, not just replies to it, so we repeat
        # the first message here
        thread_messages = {
            "messages": [
                slack_message.event,
                {
                    "ts": self.anystr("slack ts 1"),
                    "channel": self.getstr("slack channel"),
                    "text": f"<{self.anyurl('url2')}>",
                    "app_id": self.getstr("not eave app_id"),
                },
                {
                    "ts": self.anystr("slack ts 2"),
                    "channel": self.getstr("slack channel"),
                    "text": f"<{self.anyurl('url3')}>",
                    "app_id": SHARED_CONFIG.eave_slack_app_id,
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
        assert self.geturl("url1") in result
        assert self.geturl("url2") in result
        assert self.geturl("url3") not in result
