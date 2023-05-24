import re
from .base import BaseTestCase

mut = "eave.slack.brain.subscription_management"


class SubscriptionManagementMixinTest(BaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

    async def test_get_subscription(self) -> None:
        response = await self.sut.get_subscription()
        assert response
        assert response.team.id == self._data_eave_team.id
        assert response.subscription.source.platform == "slack"
        assert response.subscription.source.event == "slack_message"
        assert (
            response.subscription.source.id
            == f"{self.getstr('message.team')}#{self.getstr('message.channel')}#{self.getstr('message.thread_ts')}"
        )

    async def test_create_subscription(self) -> None:
        response = await self.sut.create_subscription()
        assert response
        assert response.team.id == self._data_eave_team.id
        assert response.subscription.source.platform == "slack"
        assert response.subscription.source.event == "slack_message"
        assert (
            response.subscription.source.id
            == f"{self.getstr('message.team')}#{self.getstr('message.channel')}#{self.getstr('message.thread_ts')}"
        )

    async def test_notify_existing_subscription_with_document_reference(self) -> None:
        await self.sut.notify_existing_subscription(subscription=self._data_subscription_response)
        mock = self._data_slack_context.client.chat_postMessage
        assert mock.call_count == 1
        assert mock.call_args.kwargs["channel"] == self.getstr("message.channel")
        assert mock.call_args.kwargs["thread_ts"] == self.getstr("message.thread_ts")
        assert re.search("I'm already watching this conversation", mock.call_args.kwargs["text"])
        assert re.search(self._data_document_reference.document_url, mock.call_args.kwargs["text"])
        assert self.logged_event(event_name="eave_sent_message")

    async def test_notify_existing_subscription_no_document_reference(self) -> None:
        self._data_subscription_response.document_reference = None

        await self.sut.notify_existing_subscription(subscription=self._data_subscription_response)

        mock = self._data_slack_context.client.chat_postMessage
        assert mock.call_count == 0
        # assert mock.call_args.kwargs["channel"] == self.getstr("message.channel")
        # assert mock.call_args.kwargs["thread_ts"] == self.getstr("message.thread_ts")
        # assert re.search("I'm currently working on the documentation", mock.call_args.kwargs["text"])
        # assert self.logged_event(event_name="eave_sent_message")
