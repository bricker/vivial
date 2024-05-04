import http
import time

import aiohttp
from google.cloud import bigquery
from google.cloud.bigquery.dataset import DatasetReference

from eave.collectors.core.datastructures import (
    BrowserEventPayload,
    DatabaseEventPayload,
    DatabaseOperation,
    DatabaseStructure,
    DataIngestRequestBody,
    EventType,
    HttpClientEventPayload,
    HttpServerEventPayload,
)
from eave.core.internal.atoms.browser_events import BrowserEventsTableHandle
from eave.core.internal.atoms.db_events import DatabaseEventsTableHandle
from eave.core.internal.atoms.http_client_events import HttpClientEventsTableHandle
from eave.core.internal.atoms.http_server_events import HttpServerEventsTableHandle
from eave.core.internal.atoms.table_handle import BigQueryTableHandle
from eave.core.internal.lib.bq_client import EAVE_INTERNAL_BIGQUERY_CLIENT
from eave.core.internal.orm.client_credentials import ClientCredentialsOrm, ClientScope
from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.headers import EAVE_CLIENT_ID_HEADER, EAVE_CLIENT_SECRET_HEADER

from .base import BaseTestCase

client = bigquery.Client(project=SHARED_CONFIG.google_cloud_project)


class TestMetabaseEmbeddingSSOEndpoints(BaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

        async with self.db_session.begin() as s:
            self._account = await self.make_account(session=s)

    async def asyncTearDown(self) -> None:
        await super().asyncTearDown()

    # async def test_metabase_embedding_sso(self) -> None:
    #     response = await self.make_request(
    #         path="/oauth/metabase",
    #         headers={
    #             EAVE_CLIENT_ID_HEADER: str(self.anyuuid("invalid client ID")),
    #             EAVE_CLIENT_SECRET_HEADER: self.anystr("invalid client secret"),
    #         },
    #         payload=DataIngestRequestBody(events={}).to_dict(),
    #     )

    #     assert response.status_code == http.HTTPStatus.OK

