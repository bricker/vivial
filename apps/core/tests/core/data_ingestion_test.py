import http
import time

import aiohttp
from google.cloud import bigquery

from eave.collectors.core.datastructures import (
    DatabaseEventPayload,
    DatabaseOperation,
    DataIngestRequestBody,
    EventType,
    HttpServerEventPayload,
)
from eave.core.internal.atoms.models.atom_types import BrowserEventAtom, DatabaseEventAtom, HttpServerEventAtom
from eave.core.internal.atoms.models.enums import HttpRequestMethod
from eave.core.internal.orm.client_credentials import ClientCredentialsOrm, ClientScope
from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.headers import EAVE_CLIENT_ID_HEADER, EAVE_CLIENT_SECRET_HEADER

from .bq_tests_base import BigQueryTestsBase

client = bigquery.Client(project=SHARED_CONFIG.google_cloud_project)


class TestDataIngestionEndpoints(BigQueryTestsBase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

    async def asyncTearDown(self) -> None:
        await super().asyncTearDown()

    async def _client_credentials_used(self) -> bool:
        async with self.db_session.begin() as s:
            c = await self.reload(s, self.client_credentials)
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
        assert not self.team_bq_dataset_exists()
        assert not (await self._client_credentials_used())

    async def test_server_ingest_invalid_scopes(self) -> None:
        async with self.db_session.begin() as s:
            ro_creds = await ClientCredentialsOrm.create(
                session=s,
                team_id=self.eave_team.id,
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
        assert not self.team_bq_dataset_exists()
        assert not (await self._client_credentials_used())

    async def test_server_ingest_valid_credentials(self) -> None:
        assert not (await self._client_credentials_used())

        response = await self.make_request(
            path="/public/ingest/server",
            headers={
                EAVE_CLIENT_ID_HEADER: str(self.client_credentials.id),
                EAVE_CLIENT_SECRET_HEADER: self.client_credentials.secret,
            },
            payload=DataIngestRequestBody(events={}).to_dict(),
        )

        assert response.status_code == http.HTTPStatus.OK
        assert await self._client_credentials_used()

    async def test_server_insert_with_no_events_doesnt_lazy_create_anything(self) -> None:
        response = await self.make_request(
            path="/public/ingest/server",
            headers={
                EAVE_CLIENT_ID_HEADER: str(self.client_credentials.id),
                EAVE_CLIENT_SECRET_HEADER: self.client_credentials.secret,
            },
            payload=DataIngestRequestBody(events={}).to_dict(),
        )

        assert response.status_code == http.HTTPStatus.OK
        assert not self.team_bq_dataset_exists()

    async def test_server_insert_lazy_creates_db_and_tables(self) -> None:
        assert not self.team_bq_dataset_exists()
        assert not self.team_bq_table_exists(DatabaseEventAtom.table_def().table_id)
        assert not self.team_bq_table_exists(HttpServerEventAtom.table_def().table_id)
        assert not self.team_bq_table_exists(BrowserEventAtom.table_def().table_id)
        assert not (await self._client_credentials_used())

        response = await self.make_request(
            path="/public/ingest/server",
            headers={
                EAVE_CLIENT_ID_HEADER: str(self.client_credentials.id),
                EAVE_CLIENT_SECRET_HEADER: self.client_credentials.secret,
            },
            payload=DataIngestRequestBody(
                events={
                    EventType.db_event: [
                        DatabaseEventPayload(
                            event_id=str(self.anyuuid()),
                            corr_ctx=None,
                            timestamp=time.time(),
                            db_name=self.anystr(),
                            statement="update my_table set a=$1, b=$2;",
                            operation=DatabaseOperation.INSERT,
                            table_name=self.anystr(),
                            statement_values=self.anydict(),
                        ).to_dict(),
                    ],
                    EventType.http_server_event: [
                        HttpServerEventPayload(
                            event_id=str(self.anyuuid()),
                            timestamp=time.time(),
                            corr_ctx=None,
                            request_method=HttpRequestMethod.GET,
                            request_url="https://api.eave.fyi/status",
                            request_headers={},
                            request_payload="{}",
                        ).to_dict(),
                    ],
                    EventType.browser_event: [
                        {"action": "click"},
                    ],
                },
            ).to_dict(),
        )

        assert response.status_code == http.HTTPStatus.OK
        assert self.team_bq_dataset_exists()
        assert self.team_bq_table_exists(DatabaseEventAtom.table_def().table_id)
        assert self.team_bq_table_exists(HttpServerEventAtom.table_def().table_id)
        assert self.team_bq_table_exists(BrowserEventAtom.table_def().table_id)
        assert await self._client_credentials_used()

    async def test_browser_insert_endpoint(self) -> None:
        assert not self.team_bq_dataset_exists()
        assert not self.team_bq_table_exists(BrowserEventAtom.table_def().table_id)
        assert not (await self._client_credentials_used())

        response = await self.make_request(
            method="POST",
            path=f"/public/ingest/browser?clientId={self.client_credentials.id}",
            headers={
                aiohttp.hdrs.ORIGIN: "https://eave.test",
            },
            payload=DataIngestRequestBody(
                events={
                    EventType.http_server_event: [  # This should be ignored by the server
                        HttpServerEventPayload(
                            event_id=str(self.anyuuid()),
                            timestamp=time.time(),
                            corr_ctx=None,
                            request_method=HttpRequestMethod.GET,
                            request_url="https://api.eave.fyi/status",
                            request_headers={},
                            request_payload="{}",
                        ).to_dict(),
                    ],
                    EventType.browser_event: [
                        {"action": "click"},
                    ],
                },
            ).to_dict(),
        )

        assert response.status_code == http.HTTPStatus.OK
        assert await self._client_credentials_used()
        assert self.team_bq_dataset_exists()
        assert self.team_bq_table_exists(BrowserEventAtom.table_def().table_id)
        assert not self.team_bq_table_exists(HttpServerEventAtom.table_def().table_id)

    async def test_browser_insert_endpoint_with_invalid_client_id(self) -> None:
        response = await self.make_request(
            method="POST",
            path=f"/public/ingest/browser?clientId={self.anyuuid()}",
            headers={
                aiohttp.hdrs.ORIGIN: "https://eave.test",
            },
            payload=DataIngestRequestBody(
                events={
                    EventType.browser_event: [
                        {"action": "click"},
                    ],
                },
            ).to_dict(),
        )

        assert response.status_code == http.HTTPStatus.UNAUTHORIZED
        assert not (await self._client_credentials_used())
        assert not self.team_bq_dataset_exists()

    async def test_browser_insert_endpoint_with_invalid_origin(self) -> None:
        response = await self.make_request(
            method="POST",
            path=f"/public/ingest/browser?clientId={self.client_credentials.id}",
            headers={
                aiohttp.hdrs.ORIGIN: self.anystr(),
            },
            payload=DataIngestRequestBody(
                events={
                    EventType.browser_event: [
                        {"action": "click"},
                    ],
                },
            ).to_dict(),
        )

        assert response.status_code == http.HTTPStatus.FORBIDDEN
        assert not (await self._client_credentials_used())
        assert not self.team_bq_dataset_exists()

    async def test_browser_ingest_invalid_scopes(self) -> None:
        async with self.db_session.begin() as s:
            ro_creds = await ClientCredentialsOrm.create(
                session=s,
                team_id=self.eave_team.id,
                description=self.anystr(),
                scope=ClientScope.read,
            )

        response = await self.make_request(
            method="POST",
            path=f"/public/ingest/browser?clientId={ro_creds.id}",
            headers={aiohttp.hdrs.ORIGIN: "https://eave.test"},
            payload=DataIngestRequestBody(events={}).to_dict(),
        )

        assert response.status_code == http.HTTPStatus.FORBIDDEN
        assert not (await self._client_credentials_used())
        assert not self.team_bq_dataset_exists()
