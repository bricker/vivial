from unittest import IsolatedAsyncioTestCase


class BaseMixin(IsolatedAsyncioTestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.addAsyncCleanup(self.cleanup)

    async def cleanup(self) -> None:
        pass
