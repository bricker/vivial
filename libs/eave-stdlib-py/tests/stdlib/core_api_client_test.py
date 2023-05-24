from eave.stdlib.test_util import UtilityBaseTestCase

class TestCoreApiClient(UtilityBaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

    async def test_alive(self) -> None:
        assert True