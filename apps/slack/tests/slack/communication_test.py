import re
import unittest.mock

from slack_sdk.errors import SlackApiError

from eave.slack.brain.message_prompts import MessageAction
from eave.stdlib.exceptions import HTTPException
from .base import BaseTestCase

class CommunicationMixinTest(BaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

    async def test_send_response(self) -> None:
        mock = self._data_slack_context.client.chat_postMessage
        assert mock.call_count == 0

        await self.sut.send_response(text=self.anystring("text"), eave_message_purpose=self.anystring("purpose"), opaque_params=self.anydict("params"))

        assert mock.call_count == 1
        assert mock.call_args.kwargs["text"] == f"<@{self._data_message.user}> {self.getstr('text')}"
        assert mock.call_args.kwargs["channel"] == self.getstr("message.channel")
        assert mock.call_args.kwargs["thread_ts"] == self.getstr("message.thread_ts")
        assert self.logged_event(event_name="eave_sent_message", opaque_params={
            "eave_message_purpose": self.getstr("purpose"),
            "eave_message_content": self.getstr("text"),
            **self.getdict("params"),
        })

    async def test_send_response_no_params(self) -> None:
        mock = self._data_slack_context.client.chat_postMessage
        assert mock.call_count == 0

        await self.sut.send_response(text=self.anystring("text"), eave_message_purpose=self.anystring("purpose"))

        assert mock.call_count == 1
        assert self.logged_event(event_name="eave_sent_message", opaque_params={
            "eave_message_purpose": self.getstr("purpose"),
            "eave_message_content": self.getstr("text"),
        })

    async def test_notify_failure(self) -> None:
        mock = self._data_slack_context.client.chat_postMessage
        assert mock.call_count == 0

        exc = HTTPException(status_code=500, request_id=self.anystring("request id"))
        await self.sut.notify_failure(e=exc)

        assert mock.call_count == 1
        assert re.search("technical issue", mock.call_args.kwargs["text"])
        assert self.logged_event(event_name="eave_sent_message", opaque_params={
            "request_id": self.getstr("request id"),
        })

    async def test_notify_failure_other_exception(self) -> None:
        mock = self._data_slack_context.client.chat_postMessage
        assert mock.call_count == 0

        exc = ValueError("test error")
        await self.sut.notify_failure(e=exc)

        assert mock.call_count == 1
        assert re.search("technical issue", mock.call_args.kwargs["text"])
        assert self.logged_event(event_name="eave_sent_message", opaque_params={
            "request_id": None,
        })

    async def test_acknowledge_receipt_with_eave_emoji(self) -> None:
        mock = self._data_slack_context.client.reactions_add
        assert mock.call_count == 0

        await self.sut.acknowledge_receipt()

        assert mock.call_count == 1
        assert mock.call_args.kwargs["name"] == "eave"
        assert mock.call_args.kwargs["channel"] == self.getstr("message.channel")
        assert mock.call_args.kwargs["timestamp"] == self.getstr("message.ts")

        assert self.logged_event(event_name="eave_acknowledged_receipt", opaque_params={
            "reaction": "eave",
        })

    async def test_acknowledge_receipt_with_no_eave_emoji(self) -> None:
        mock = self._data_slack_context.client.reactions_add
        mock_response = { "error": "invalid_name" }
        mock.side_effect = [SlackApiError(message=self.anystring(), response=mock_response), None]
        assert mock.call_count == 0

        await self.sut.acknowledge_receipt()

        assert mock.call_count == 2
        assert mock.call_args_list[0].kwargs["name"] == "eave"
        assert mock.call_args_list[1].kwargs["name"] == "thumbsup"

        assert self.logged_event(event_name="eave_acknowledged_receipt", opaque_params={
            "reaction": "thumbsup",
        })

        assert not self.logged_event(event_name="eave_acknowledged_receipt", opaque_params={
            "reaction": "eave",
        })

    async def test_acknowledge_receipt_with_some_other_error(self) -> None:
        mock = self._data_slack_context.client.reactions_add
        mock_response = { "error": self.anystring() }
        mock.side_effect = SlackApiError(message=self.anystring(), response=mock_response)

        with self.assertRaises(SlackApiError):
            await self.sut.acknowledge_receipt()
