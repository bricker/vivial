from typing import override
from httpx import ASGITransport, AsyncClient
from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.test_helpers.base_mixin import BaseMixin
import eave.core.app

class HTTPClientMixin(BaseMixin):
    httpclient: AsyncClient # pyright: ignore [reportUninitializedInstanceVariable]

    @override
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

        transport = ASGITransport(
            app=eave.core.app.app,
            raise_app_exceptions=True,
        )
        self.httpclient = AsyncClient(
            base_url=SHARED_CONFIG.eave_api_base_url_public,
            transport=transport,
        )

    @override
    async def asyncTearDown(self):
        await super().asyncTearDown()
        await self.httpclient.aclose()
