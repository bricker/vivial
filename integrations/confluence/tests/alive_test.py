import tests
import mockito
import mockito.matchers
from tests.base import BaseTestCase

class TestAlive(BaseTestCase):
    async def test_alive(self) -> None:
        self.assert_(True)
