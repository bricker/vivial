from .base import BaseTestCase


class TestAlive(BaseTestCase):
    async def test_alive(self) -> None:
        self.assert_(True)
