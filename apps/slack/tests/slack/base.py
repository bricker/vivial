import unittest
from typing import Optional, TypeVar
from uuid import uuid4

T = TypeVar("T")


class BaseTestCase(unittest.IsolatedAsyncioTestCase):
    _testdata = dict[str, str]()

    def __init__(self, methodName: str) -> None:
        super().__init__(methodName)
        self.maxDiff = None

    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self._testdata.clear()

    async def asyncTearDown(self) -> None:
        await super().asyncTearDown()

    def unwrap(self, value: Optional[T]) -> T:
        self.assertIsNotNone(value)
        assert value is not None
        return value

    def anystring(self, name: str = str(uuid4())) -> str:
        if name not in self._testdata:
            data = str(uuid4())
            self._testdata[name] = data

        return self._testdata[name]
