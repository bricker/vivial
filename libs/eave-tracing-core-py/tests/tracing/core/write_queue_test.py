from eave.stdlib.test_util import UtilityBaseTestCase


class WriteQueueTest(UtilityBaseTestCase):
    async def asyncSetUp(self):
        await super().asyncSetUp()

    async def test_alive(self):
        assert True
