import http
import time

import aiohttp
from google.cloud import bigquery

from eave.collectors.core.datastructures import (
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
from eave.core.internal.lib.bq_client import EAVE_INTERNAL_BIGQUERY_CLIENT
from eave.core.internal.orm.client_credentials import ClientCredentialsOrm, ClientScope
from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.headers import EAVE_CLIENT_ID_HEADER, EAVE_CLIENT_SECRET_HEADER

from eave.core.internal.orm.team import bq_dataset_id

from .base import BaseTestCase

client = bigquery.Client(project=SHARED_CONFIG.google_cloud_project)


class TestDataIngestionEndpoints(BaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

        async with self.db_session.begin() as s:
            self._team = await self.make_team(session=s)
            self._client_credentials = await ClientCredentialsOrm.create(
                session=s,
                team_id=self._team.id,
                description=self.anystr(),
                scope=ClientScope.readwrite,
            )

        client.delete_dataset(
            dataset=bq_dataset_id(self._team.id),
            delete_contents=True,
            not_found_ok=True,
        )

    async def asyncTearDown(self) -> None:
        await super().asyncTearDown()
        client.delete_dataset(
            dataset=bq_dataset_id(self._team.id),
            delete_contents=True,
            not_found_ok=True,
        )

    def _bq_team_dataset_exists(self) -> bool:
        try:
            dataset = client.get_dataset(dataset_ref=bq_dataset_id(self._team.id))
        except Exception as e:
            print(f"Google Cloud Error: {e}")
            return False

        return dataset is not None

    def _bq_table_exists(self, table_name: str) -> bool:
        table = EAVE_INTERNAL_BIGQUERY_CLIENT.get_table_or_none(
            dataset_id=bq_dataset_id(self._team.id), table_id=table_name
        )
        return table is not None

    async def _client_credentials_used(self) -> bool:
        async with self.db_session.begin() as s:
            c = await self.reload(s, self._client_credentials)
            assert c
            return c.last_used is not None

    async def test_server_ingest_invalid_credentials(self) -> None:
        response = await self.make_request(
            path="/public/ingest/server",
            headers={
                EAVE_CLIENT_ID_HEADER: str(self.anyuuid("invalid client ID")),
                EAVE_CLIENT_SECRET_HEADER: self.anystr("invalid client secret"),
            },
            payload=DataIngestRequestBody(events={}).to_dict(),
        )

        assert response.status_code == http.HTTPStatus.UNAUTHORIZED
        assert not self._bq_team_dataset_exists()
        assert not (await self._client_credentials_used())

    async def test_server_ingest_invalid_scopes(self) -> None:
        async with self.db_session.begin() as s:
            ro_creds = await ClientCredentialsOrm.create(
                session=s,
                team_id=self._team.id,
                description=self.anystr(),
                scope=ClientScope.read,
            )

        response = await self.make_request(
            path="/public/ingest/server",
            headers={
                EAVE_CLIENT_ID_HEADER: str(ro_creds.id),
                EAVE_CLIENT_SECRET_HEADER: ro_creds.secret,
            },
            payload=DataIngestRequestBody(events={}).to_dict(),
        )

        assert response.status_code == http.HTTPStatus.FORBIDDEN
        assert not self._bq_team_dataset_exists()
        assert not (await self._client_credentials_used())

    async def test_server_ingest_valid_credentials(self) -> None:
        assert not (await self._client_credentials_used())

        response = await self.make_request(
            path="/public/ingest/server",
            headers={
                EAVE_CLIENT_ID_HEADER: str(self._client_credentials.id),
                EAVE_CLIENT_SECRET_HEADER: self._client_credentials.secret,
            },
            payload=DataIngestRequestBody(events={}).to_dict(),
        )

        assert response.status_code == http.HTTPStatus.OK
        assert await self._client_credentials_used()

    async def test_server_insert_with_no_events_doesnt_lazy_create_anything(self) -> None:
        response = await self.make_request(
            path="/public/ingest/server",
            headers={
                EAVE_CLIENT_ID_HEADER: str(self._client_credentials.id),
                EAVE_CLIENT_SECRET_HEADER: self._client_credentials.secret,
            },
            payload=DataIngestRequestBody(events={}).to_dict(),
        )

        assert response.status_code == http.HTTPStatus.OK
        assert not self._bq_team_dataset_exists()

    async def test_server_insert_lazy_creates_db_and_tables(self) -> None:
        assert not self._bq_team_dataset_exists()
        assert not self._bq_table_exists(DatabaseEventsTableHandle.table_def.table_id)
        assert not self._bq_table_exists(HttpServerEventsTableHandle.table_def.table_id)
        assert not self._bq_table_exists(HttpClientEventsTableHandle.table_def.table_id)
        assert not self._bq_table_exists(BrowserEventsTableHandle.table_def.table_id)
        assert not (await self._client_credentials_used())

        response = await self.make_request(
            path="/public/ingest/server",
            headers={
                EAVE_CLIENT_ID_HEADER: str(self._client_credentials.id),
                EAVE_CLIENT_SECRET_HEADER: self._client_credentials.secret,
            },
            payload=DataIngestRequestBody(
                events={
                    EventType.db_event: [
                        DatabaseEventPayload(
                            context=None,
                            db_structure=DatabaseStructure.SQL,
                            timestamp=time.time(),
                            db_name=self.anystr(),
                            statement="update my_table set a=$1, b=$2;",
                            operation=DatabaseOperation.INSERT,
                            table_name=self.anystr(),
                            parameters={
                                "a": self.anystr(),
                                "b": self.anystr(),
                            },
                        ).to_dict(),
                    ],
                    EventType.http_server_event: [
                        HttpServerEventPayload(
                            timestamp=time.time(),
                            context=None,
                            request_method="GET",
                            request_url="https://api.eave.fyi/status",
                            request_headers={},
                            request_payload="{}",
                        ).to_dict(),
                    ],
                    EventType.http_client_event: [
                        HttpClientEventPayload(
                            timestamp=time.time(),
                            context=None,
                            request_method="GET",
                            request_url="https://api.eave.fyi/status",
                            request_headers={},
                            request_payload="{}",
                        ).to_dict(),
                    ],
                    EventType.browser_event: [
                        {
                            "context": None,
                            "event": {
                                "action": "click",
                            },
                        },
                    ],
                },
            ).to_dict(),
        )

        assert response.status_code == http.HTTPStatus.OK
        assert self._bq_team_dataset_exists()
        assert self._bq_table_exists(DatabaseEventsTableHandle.table_def.table_id)
        assert self._bq_table_exists(HttpServerEventsTableHandle.table_def.table_id)
        assert self._bq_table_exists(HttpClientEventsTableHandle.table_def.table_id)
        assert self._bq_table_exists(BrowserEventsTableHandle.table_def.table_id)
        assert await self._client_credentials_used()

    async def test_browser_insert_endpoint(self) -> None:
        assert not self._bq_team_dataset_exists()
        assert not self._bq_table_exists(BrowserEventsTableHandle.table_def.table_id)
        assert not (await self._client_credentials_used())

        response = await self.make_request(
            path="/public/ingest/browser",
            headers={
                EAVE_CLIENT_ID_HEADER: str(self._client_credentials.id),
                aiohttp.hdrs.ORIGIN: self._team.allowed_origins[0],
            },
            payload=DataIngestRequestBody(
                events={
                    EventType.http_server_event: [  # This should be ignored by the server
                        HttpServerEventPayload(
                            timestamp=time.time(),
                            context=None,
                            request_method="GET",
                            request_url="https://api.eave.fyi/status",
                            request_headers={},
                            request_payload="{}",
                        ).to_dict(),
                    ],
                    EventType.browser_event: [
                        {
                            "context": None,
                            "event": {
                                "action": "click",
                            },
                        },
                    ],
                },
            ).to_dict(),
        )

        assert response.status_code == http.HTTPStatus.OK
        assert await self._client_credentials_used()
        assert self._bq_team_dataset_exists()
        assert self._bq_table_exists(BrowserEventsTableHandle.table_def.table_id)
        assert not self._bq_table_exists(HttpServerEventsTableHandle.table_def.table_id)

    async def test_browser_insert_endpoint_with_invalid_client_id(self) -> None:
        response = await self.make_request(
            path="/public/ingest/browser",
            headers={
                EAVE_CLIENT_ID_HEADER: str(self.anyuuid()),
                aiohttp.hdrs.ORIGIN: self._team.allowed_origins[0],
            },
            payload=DataIngestRequestBody(
                events={
                    EventType.browser_event: [
                        {
                            "context": None,
                            "event": {
                                "action": "click",
                            },
                        },
                    ],
                },
            ).to_dict(),
        )

        assert response.status_code == http.HTTPStatus.UNAUTHORIZED
        assert not (await self._client_credentials_used())
        assert not self._bq_team_dataset_exists()

    async def test_browser_insert_endpoint_with_invalid_origin(self) -> None:
        response = await self.make_request(
            path="/public/ingest/browser",
            headers={
                EAVE_CLIENT_ID_HEADER: str(self._client_credentials.id),
                aiohttp.hdrs.ORIGIN: self.anystr(),
            },
            payload=DataIngestRequestBody(
                events={
                    EventType.browser_event: [
                        {
                            "context": None,
                            "event": {
                                "action": "click",
                            },
                        },
                    ],
                },
            ).to_dict(),
        )

        assert response.status_code == http.HTTPStatus.FORBIDDEN
        assert not (await self._client_credentials_used())
        assert not self._bq_team_dataset_exists()

    async def test_browser_ingest_invalid_scopes(self) -> None:
        async with self.db_session.begin() as s:
            ro_creds = await ClientCredentialsOrm.create(
                session=s,
                team_id=self._team.id,
                description=self.anystr(),
                scope=ClientScope.read,
            )

        response = await self.make_request(
            path="/public/ingest/browser",
            headers={EAVE_CLIENT_ID_HEADER: str(ro_creds.id), aiohttp.hdrs.ORIGIN: self._team.allowed_origins[0]},
            payload=DataIngestRequestBody(events={}).to_dict(),
        )

        assert response.status_code == http.HTTPStatus.FORBIDDEN
        assert not (await self._client_credentials_used())
        assert not self._bq_team_dataset_exists()
