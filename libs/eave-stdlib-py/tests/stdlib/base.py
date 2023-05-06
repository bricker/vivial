import unittest
from typing import TypeVar

T = TypeVar("T")


async def mock_coroutine(value: T) -> T:
    return value


class BaseTestCase(unittest.IsolatedAsyncioTestCase):
    def __init__(self, methodName: str) -> None:
        super().__init__(methodName)
        self.maxDiff = None

    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

    async def asyncTearDown(self) -> None:
        await super().asyncTearDown()
