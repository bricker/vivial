from unittest import IsolatedAsyncioTestCase

from .base import BaseTestCase


class IngestApiTest(BaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

    async def test_send_batch(self) -> None:
        self.fail("TODO")
