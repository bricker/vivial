from http import HTTPStatus

from eave.stdlib.logging import LogContext
import google.oauth2.credentials
from aiohttp.hdrs import AUTHORIZATION
from httpx import Response

from eave.core.internal.atoms.browser_events import BrowserEventsTableHandle
from eave.core.internal.atoms.record_fields import GeoRecordField
from eave.core.internal.oauth.google import GoogleOAuthV2GetResponse
from eave.core.internal.orm.account import AccountOrm
from eave.stdlib.auth_cookies import (
    EAVE_ACCESS_TOKEN_COOKIE_NAME,
    EAVE_ACCOUNT_ID_COOKIE_NAME,
)
from eave.stdlib.core_api.models.account import AuthProvider
from eave.stdlib.core_api.operations.account import GetMyAccountRequest
from eave.stdlib.headers import EAVE_ACCOUNT_ID_HEADER

from .base import BaseTestCase

empty_ctx = LogContext()

class TestBrowserEventsAtoms(BigQueryTestsBase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

    async def test_insert(self) -> None:
        table = BrowserEventsTableHandle(team=self._team)
        await table.insert_with_geolocation(
            events=[BrowserEventPayload()]
            )],
            client_ip="1.2.3.4",
            geolocation=GeoRecordField(
                region="US",
                subdivision="CA",
                city="Palo Alto",
                coordinates="37.41111281622952, -122.12322865137392",
            ),
            ctx=empty_ctx,
        )
