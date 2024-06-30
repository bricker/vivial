from unittest import IsolatedAsyncioTestCase


class IngestApiTest(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

    async def test_send_batch(self) -> None:
        self.fail("not implemented")
