from unittest import IsolatedAsyncioTestCase


class WriteQueueTest(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

    async def test_write_queue(self) -> None:
        self.fail("not implemented")
