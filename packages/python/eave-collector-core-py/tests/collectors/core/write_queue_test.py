
from .base import BaseTestCase


class WriteQueueTest(BaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

    async def test_write_queue(self) -> None:
        self.fail("TODO")
