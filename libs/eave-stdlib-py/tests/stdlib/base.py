from eave.stdlib.testing_util import UtilityBaseTestCase


class StdlibBaseTestCase(UtilityBaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
