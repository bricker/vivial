import unittest.mock
from unittest.mock import AsyncMock
from httpx import AsyncClient
from slack_bolt.async_app import AsyncBoltContext
from slack_sdk.web.async_client import AsyncWebClient
from eave.slack.config import app_config
import eave.slack.app
from eave.slack.slack_models import SlackMessage
from eave.slack.brain.core import Brain
from eave.stdlib.core_api.enums import DocumentPlatform
from eave.stdlib.core_api.models import DocumentReference, Subscription, Team
from eave.stdlib.core_api.operations import GetSubscription
from eave.stdlib.test_util import UtilityBaseTestCase


class BaseTestCase(UtilityBaseTestCase):
    def __init__(self, methodName: str) -> None:
        super().__init__(methodName)
        self.addAsyncCleanup(self.cleanup)

    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        # transport = httpx.ASGITransport(
        #     app=eave.slack.app.api,  # type:ignore
        #     raise_app_exceptions=True,
        # )

        self.httpclient = AsyncClient(
            app=eave.slack.app.api,
            base_url=app_config.eave_apps_base,
        )

        self._data_slack_context = AsyncMock(spec=AsyncBoltContext)
        self._data_slack_context.client = AsyncMock(spec=AsyncWebClient)
        self._data_message = SlackMessage(
            data={
                "ts": self.anystring("message.ts"),
                "team": self.anystring("message.team"),
                "channel": self.anystring("message.channel"),
                "thread_ts": self.anystring("message.thread_ts"),
                "user": self.anystring("message.user"),
            },
            slack_context=self._data_slack_context,
        )

        self._data_eave_team = Team(
            id=self.anyuuid(), name=self.anystring(), document_platform=DocumentPlatform.confluence
        )

        self._data_subscription = Subscription(
            id=self.anyuuid(),
            document_reference_id=self.anyuuid(),
            source=self._data_message.subscription_source,
        )

        self._data_document_reference = DocumentReference(
            id=self.anyuuid(),
            document_id=self.anystring(),
            document_url=self.anystring(),
        )

        self._data_subscription_response = GetSubscription.ResponseBody(
            team=self._data_eave_team,
            subscription=self._data_subscription,
            document_reference=self._data_document_reference,
        )

        self.patch(
            name="get subscription",
            patch=unittest.mock.patch(
                "eave.stdlib.core_api.client.get_subscription", return_value=self._data_subscription_response
            ),
        )
        self.patch(
            name="create subscription",
            patch=unittest.mock.patch(
                "eave.stdlib.core_api.client.create_subscription", return_value=self._data_subscription_response
            ),
        )
        self.patch(
            name="delete subscription",
            patch=unittest.mock.patch("eave.stdlib.core_api.client.delete_subscription", return_value=None),
        )

        self.sut = Brain(message=self._data_message, eave_team=self._data_eave_team)

    async def asyncTearDown(self) -> None:
        await super().asyncTearDown()

    async def cleanup(self) -> None:
        await super().cleanup()
        await self.httpclient.aclose()
