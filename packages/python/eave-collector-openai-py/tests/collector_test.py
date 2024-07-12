import os
import unittest

from openai import AsyncOpenAI, OpenAI

from eave.collectors.core.datastructures import OpenAIChatCompletionEventPayload, StackFrame
from eave.collectors.core.test_util import EphemeralWriteQueue
from eave.collectors.openai.private.collector import OpenAICollector


class OpenAICollectorTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

        self._write_queue = EphemeralWriteQueue()
        self._sync_collector = OpenAICollector(write_queue=self._write_queue)
        self._async_collector = OpenAICollector(write_queue=self._write_queue)
        self.sync_client = OpenAI(
            # TODO: fetch for test? they have a dummy client?
            api_key=os.environ.get("OPENAI_API_KEY"),
        )
        self.async_client = AsyncOpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
        )
        self._sync_collector.instrument(client=self.sync_client)
        self._async_collector.instrument(client=self.async_client)

    async def asyncTearDown(self) -> None:
        await super().asyncTearDown()

        self._sync_collector.uninstrument()
        self._async_collector.uninstrument()

    def test_double_instrumentation_doesnt_double_events(self) -> None:
        # GIVEN a client/module is instrumented a 2nd time
        # (first call in asyncSetUp)
        self._sync_collector.instrument(client=self.sync_client)

        # WHEN a instrumented func is called
        _ = self.sync_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "Say this is a test",
                }
            ],
            model="gpt-3.5-turbo",
            user="mock_user_id",
        )

        # THEN only 1 event is created
        assert len(self._write_queue.queue) == 1
        e = self._write_queue.queue[0]
        assert isinstance(e, OpenAIChatCompletionEventPayload)
        assert e.completion_user_id == "mock_user_id"
        assert e.prompt_tokens and e.prompt_tokens > 0
        assert e.completion_tokens and e.completion_tokens > 0
        assert e.openai_request is not None
        assert e.openai_request.start_timestamp is not None
        assert e.openai_request.end_timestamp is not None
        assert e.openai_request.request_params is not None

    def test_sync_chat_completion_captured(self) -> None:
        _ = self.sync_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "Say this is a test",
                }
            ],
            model="gpt-3.5-turbo",
            user="mock_user_id",
        )

        assert len(self._write_queue.queue) == 1
        e = self._write_queue.queue[0]
        assert isinstance(e, OpenAIChatCompletionEventPayload)
        assert e.completion_user_id == "mock_user_id"
        assert e.prompt_tokens and e.prompt_tokens > 0
        assert e.completion_tokens and e.completion_tokens > 0

    async def test_async_chat_completion_captured(self) -> None:
        _ = await self.async_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "Say this is a test",
                }
            ],
            model="gpt-3.5-turbo",
            user="mock_user_id",
        )

        assert len(self._write_queue.queue) == 1
        e = self._write_queue.queue[0]
        assert isinstance(e, OpenAIChatCompletionEventPayload)
        assert e.completion_user_id == "mock_user_id"
        assert e.prompt_tokens and e.prompt_tokens > 0
        assert e.completion_tokens and e.completion_tokens > 0

    async def test_sync_chat_completion_streaming_captured(self) -> None:
        stream = self.sync_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "Say this is a test",
                }
            ],
            model="gpt-3.5-turbo",
            user="mock_user_id",
            stream=True,
        )

        # consume stream
        list(stream)

        assert len(self._write_queue.queue) == 1
        e = self._write_queue.queue[0]
        assert isinstance(e, OpenAIChatCompletionEventPayload)
        assert e.completion_user_id == "mock_user_id"
        assert e.prompt_tokens and e.prompt_tokens > 0
        assert e.completion_tokens and e.completion_tokens > 0

    async def test_async_chat_completion_streaming_captured(self) -> None:
        stream = await self.async_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "Say this is a test",
                }
            ],
            model="gpt-3.5-turbo",
            user="mock_user_id",
            stream=True,
            stream_options={"include_usage": False},
        )

        # consume stream
        async for _ in stream:
            ...

        assert len(self._write_queue.queue) == 1
        e = self._write_queue.queue[0]
        assert isinstance(e, OpenAIChatCompletionEventPayload)
        assert e.completion_user_id == "mock_user_id"
        assert e.prompt_tokens and e.prompt_tokens > 0
        assert e.completion_tokens and e.completion_tokens > 0

    async def test_stack_frame_capture(self) -> None:
        def first_significant_frame() -> None:
            self.sync_client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": "Say this is a test",
                    }
                ],
                model="gpt-3.5-turbo",
            )

        def second_significant_frame() -> None:
            first_significant_frame()

        second_significant_frame()

        assert len(self._write_queue.queue) == 1
        e = self._write_queue.queue[0]
        assert isinstance(e, OpenAIChatCompletionEventPayload)
        assert e.stack_frames is not None
        assert len(e.stack_frames) == 10
        assert e.stack_frames[0] == StackFrame(filename=__file__, function="first_significant_frame")
        assert e.stack_frames[1] == StackFrame(filename=__file__, function="second_significant_frame")
        assert e.stack_frames[2] == StackFrame(filename=__file__, function="test_stack_frame_capture")

    async def test_uninstrumentation(self) -> None:
        _ = self.sync_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "Say this is a test",
                }
            ],
            model="gpt-3.5-turbo",
            user="mock_user_id",
        )

        assert len(self._write_queue.queue) == 1
        e = self._write_queue.queue[0]
        assert isinstance(e, OpenAIChatCompletionEventPayload)
        assert e.completion_user_id == "mock_user_id"
        assert e.prompt_tokens and e.prompt_tokens > 0
        assert e.completion_tokens and e.completion_tokens > 0

        _ = await self.async_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "Say this is a test",
                }
            ],
            model="gpt-3.5-turbo",
            user="mock_user_id",
        )

        assert len(self._write_queue.queue) == 2
        e = self._write_queue.queue[1]
        assert isinstance(e, OpenAIChatCompletionEventPayload)
        assert e.completion_user_id == "mock_user_id"
        assert e.prompt_tokens and e.prompt_tokens > 0
        assert e.completion_tokens and e.completion_tokens > 0

        self._sync_collector.uninstrument()
        self._async_collector.uninstrument()

        _ = self.sync_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "Say this is a test",
                }
            ],
            model="gpt-3.5-turbo",
            user="mock_user_id",
        )
        _ = await self.async_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "Say this is a test",
                }
            ],
            model="gpt-3.5-turbo",
            user="mock_user_id",
        )

        assert len(self._write_queue.queue) == 2, "Events were sent to the write queue after uninstrumentation"
