import os
import unittest
from eave.collectors.core.test_util import EphemeralWriteQueue
from eave.collectors.openai.private.collector import OpenAICollector
from openai import OpenAI

from eave.core.internal.atoms.models.atom_types import OpenAIChatCompletionAtom


class OpenAICollectorTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

        self._write_queue = EphemeralWriteQueue()
        self._collector = OpenAICollector(write_queue=self._write_queue)
        self.client = OpenAI(
            # TODO: fetch for test? they have a dummy client?
            api_key=os.environ.get("OPENAI_API_KEY"),
        )
        self._collector.instrument(client=self.client)

    async def test_chat_completion_captured(self) -> None:
        _ = self.client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "Say this is a test",
                }
            ],
            model="gpt-3.5-turbo",
        )

        assert len(self._write_queue.queue) == 1
        e = self._write_queue.queue[0]
        assert isinstance(e, OpenAIChatCompletionAtom)
