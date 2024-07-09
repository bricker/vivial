import os
import unittest

from openai import AsyncOpenAI, OpenAI

from eave.collectors.core.datastructures import OpenAIChatCompletionEventPayload
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

    async def test_sync_chat_completion_captured(self) -> None:
        _ = self.sync_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "Say this is a test",
                }
            ],
            model="gpt-3.5-turbo",
            user="mock_user_id",
            max_tokens=400,
        )

        assert len(self._write_queue.queue) == 1
        e = self._write_queue.queue[0]
        assert isinstance(e, OpenAIChatCompletionEventPayload)
        assert e.max_tokens == 400
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
            max_tokens=400,
        )

        assert len(self._write_queue.queue) == 1
        e = self._write_queue.queue[0]
        assert isinstance(e, OpenAIChatCompletionEventPayload)
        assert e.max_tokens == 400
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
            max_tokens=400,
            stream=True,
        )

        # consume stream
        list(stream)

        assert len(self._write_queue.queue) == 1
        e = self._write_queue.queue[0]
        assert isinstance(e, OpenAIChatCompletionEventPayload)
        assert e.max_tokens == 400
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
            max_tokens=400,
            stream=True,
            stream_options={"include_usage": False},
        )

        # consume stream
        async for _ in stream:
            ...

        assert len(self._write_queue.queue) == 1
        e = self._write_queue.queue[0]
        assert isinstance(e, OpenAIChatCompletionEventPayload)
        assert e.max_tokens == 400
        assert e.completion_user_id == "mock_user_id"
        assert e.prompt_tokens and e.prompt_tokens > 0
        assert e.completion_tokens and e.completion_tokens > 0

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
            max_tokens=400,
        )

        assert len(self._write_queue.queue) == 1
        e = self._write_queue.queue[0]
        assert isinstance(e, OpenAIChatCompletionEventPayload)
        assert e.max_tokens == 400
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
            max_tokens=400,
        )

        assert len(self._write_queue.queue) == 2
        e = self._write_queue.queue[1]
        assert isinstance(e, OpenAIChatCompletionEventPayload)
        assert e.max_tokens == 400
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
            max_tokens=400,
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
            max_tokens=400,
        )

        assert len(self._write_queue.queue) == 2, "Events were sent to the write queue after uninstrumentation"
