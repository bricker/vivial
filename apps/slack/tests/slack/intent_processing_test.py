import re
import unittest.mock

from eave.slack.brain.message_prompts import MessageAction
from .base import BaseTestCase

mut = "eave.slack.brain.subscription_management"

class IntentProcessingMixinTest(BaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

    async def test_handle_action_CREATE_DOCUMENTATION(self) -> None:
        self.sut.create_documentation_and_subscribe = unittest.mock.AsyncMock()
        await self.sut.handle_action(message_action=MessageAction.CREATE_DOCUMENTATION)
        assert self.sut.create_documentation_and_subscribe.call_count == 1

    async def test_handle_action_WATCH(self) -> None:
        self.sut.create_documentation_and_subscribe = unittest.mock.AsyncMock()
        await self.sut.handle_action(message_action=MessageAction.WATCH)
        assert self.sut.create_documentation_and_subscribe.call_count == 1

    async def test_handle_action_UNWATCH(self) -> None:
        self.sut.unwatch_conversation = unittest.mock.AsyncMock()
        await self.sut.handle_action(message_action=MessageAction.UNWATCH)
        assert self.sut.unwatch_conversation.call_count == 1

    async def test_handle_action_SEARCH_DOCUMENTATION(self) -> None:
        self.sut.search_documentation = unittest.mock.AsyncMock()
        await self.sut.handle_action(message_action=MessageAction.SEARCH_DOCUMENTATION)
        assert self.sut.search_documentation.call_count == 1

    async def test_handle_action_UPDATE_DOCUMENTATION(self) -> None:
        self.sut.update_documentation = unittest.mock.AsyncMock()
        await self.sut.handle_action(message_action=MessageAction.UPDATE_DOCUMENTATION)
        assert self.sut.update_documentation.call_count == 1

    async def test_handle_action_REFINE_DOCUMENTATION(self) -> None:
        self.sut.refine_documentation = unittest.mock.AsyncMock()
        await self.sut.handle_action(message_action=MessageAction.REFINE_DOCUMENTATION)
        assert self.sut.refine_documentation.call_count == 1

    async def test_handle_action_DELETE_DOCUMENTATION(self) -> None:
        self.sut.archive_documentation = unittest.mock.AsyncMock()
        await self.sut.handle_action(message_action=MessageAction.DELETE_DOCUMENTATION)
        assert self.sut.archive_documentation.call_count == 1

    async def test_handle_action_UNKNOWN(self) -> None:
        self.sut.handle_unknown_request = unittest.mock.AsyncMock()
        await self.sut.handle_action(message_action=MessageAction.UNKNOWN)
        assert self.sut.handle_unknown_request.call_count == 1

    async def test_handle_action_NONE(self) -> None:
        # The NONE action doesn't do anything, the goal here is just to run the path to make sure no errors.
        self.sut.handle_unknown_request = unittest.mock.AsyncMock()
        await self.sut.handle_action(message_action=MessageAction.NONE)
        assert self.sut.handle_unknown_request.call_count == 0


    async def test_create_documentation_and_subscribe_with_existing_subscription(self) -> None:
        assert self.get_mock("create subscription").call_count == 0

        await self.sut.handle_action(message_action=MessageAction.CREATE_DOCUMENTATION)

        assert self.get_mock("create subscription").call_count == 0
        mock = self._data_slack_context.client.chat_postMessage
        assert mock.call_count == 1
        assert re.search(self._data_document_reference.document_url, mock.call_args.kwargs["text"])

    async def test_create_documentation_and_subscribe_with_no_subscription(self) -> None:
        self.sut.create_documentation = unittest.mock.AsyncMock()
        self.get_mock("get subscription").return_value = None
        assert len(self.sut.subscriptions) == 0

        await self.sut.handle_action(message_action=MessageAction.CREATE_DOCUMENTATION)

        assert len(self.sut.subscriptions) == 1
        assert self.get_mock("get subscription").call_count == 1
        assert self.get_mock("create subscription").call_count == 1
        assert self.sut.create_documentation.call_count == 1

    async def test_unknown_request_with_existing_subscription_and_document_reference(self) -> None:
        assert len(self.sut.subscriptions) == 0

        await self.sut.handle_action(message_action=MessageAction.UNKNOWN)

        assert len(self.sut.subscriptions) == 0
        assert self.logged_event(event_name="eave_received_unknown_request")
        assert self.logged_event(event_name="eave_sent_message")

        slackmock = self._data_slack_context.client.chat_postMessage
        assert slackmock.call_count == 1
        assert re.search("I haven't been trained", slackmock.call_args.kwargs["text"])
        assert re.search(self._data_document_reference.document_url, slackmock.call_args.kwargs["text"])

    async def test_unknown_request_with_existing_subscription_and_no_document_reference(self) -> None:
        self._data_subscription_response.document_reference = None
        assert len(self.sut.subscriptions) == 0

        await self.sut.handle_action(message_action=MessageAction.UNKNOWN)

        assert len(self.sut.subscriptions) == 0
        assert self.logged_event(event_name="eave_received_unknown_request")
        assert self.logged_event(event_name="eave_sent_message")

        slackmock = self._data_slack_context.client.chat_postMessage
        assert slackmock.call_count == 1
        assert re.search("I'm currently working on", slackmock.call_args.kwargs["text"])
        assert not re.search(self._data_document_reference.document_url, slackmock.call_args.kwargs["text"])

    async def test_unknown_request_with_no_subscription(self) -> None:
        self.get_mock("get subscription").return_value = None
        assert len(self.sut.subscriptions) == 0

        await self.sut.handle_action(message_action=MessageAction.UNKNOWN)

        assert len(self.sut.subscriptions) == 0
        assert self.logged_event(event_name="eave_received_unknown_request")
        assert self.logged_event(event_name="eave_sent_message")

        slackmock = self._data_slack_context.client.chat_postMessage
        assert slackmock.call_count == 1
        assert re.search("I haven't been trained", slackmock.call_args.kwargs["text"])
        assert not re.search(self._data_document_reference.document_url, slackmock.call_args.kwargs["text"])

    async def test_unwatch_conversation(self) -> None:
        assert self.get_mock("delete subscription").call_count == 0

        await self.sut.handle_action(message_action=MessageAction.UNWATCH)

        assert self.get_mock("delete subscription").call_count == 1
        assert self.logged_event(event_name="eave_unwatched_conversation")
