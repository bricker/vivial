from httpx import AsyncClient
import httpx
from eave.slack.config import app_config
import eave.slack.app
from eave.stdlib.test_util import UtilityBaseTestCase


class BaseTestCase(UtilityBaseTestCase):
    def __init__(self, methodName: str) -> None:
        super().__init__(methodName)
        self.addAsyncCleanup(self.cleanup)

    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        transport = httpx.ASGITransport(
            app=eave.slack.app.api,  # type:ignore
            raise_app_exceptions=True,
        )

        self.httpclient = AsyncClient(
            transport=transport,
            base_url=app_config.eave_apps_base,
        )

    async def asyncTearDown(self) -> None:
        await super().asyncTearDown()

    async def cleanup(self) -> None:
        await super().cleanup()
        await self.httpclient.aclose()
