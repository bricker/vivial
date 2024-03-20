from eave.stdlib.testing_util import UtilityBaseTestCase


class WriteQueueTest(UtilityBaseTestCase):
    async def asyncSetUp(self):
        await super().asyncSetUp()

    async def test_alive(self):
        assert True
