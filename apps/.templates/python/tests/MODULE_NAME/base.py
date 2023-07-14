import unittest.mock
from unittest.mock import AsyncMock
from httpx import AsyncClient
from eave.stdlib.core_api.models.subscriptions import DocumentReference, Subscription
from eave.stdlib.core_api.models.team import DocumentPlatform
from eave.stdlib.core_api.operations.subscriptions import GetSubscriptionRequest
from eave.stdlib.core_api.models.team import Team
from eave.stdlib.logging import LogContext
from eave.stdlib.test_util import UtilityBaseTestCase
import eave.{{module_name}}.app

class BaseTestCase(UtilityBaseTestCase):
    def __init__(self, methodName: str) -> None:
        super().__init__(methodName)
        self.addAsyncCleanup(self.cleanup)

    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

        self.eave_ctx = LogContext()
        self.httpclient = AsyncClient(
            app=eave.{{module_name}}.app.app,
            base_url="https://apps.eave.tests",
        )

    async def asyncTearDown(self) -> None:
        await super().asyncTearDown()

    async def cleanup(self) -> None:
        await super().cleanup()
        await self.httpclient.aclose()
