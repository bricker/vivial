import json
import unittest.mock
from datetime import datetime
from typing import Any

class CollectorTestBase(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()


    async def test_before_cursor_execute(self):
        pass