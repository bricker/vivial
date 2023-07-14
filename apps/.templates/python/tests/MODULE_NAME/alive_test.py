from .base import BaseTestCase


class AliveTest(BaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

    async def test_alive(self) -> None:
        assert True
