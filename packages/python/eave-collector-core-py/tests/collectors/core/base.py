import os
import unittest


class BaseTestCase(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        os.environ["EAVE_CREDENTIALS"] = "abc:123"
        await super().asyncSetUp()
