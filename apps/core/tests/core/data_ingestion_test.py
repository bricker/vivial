from datetime import datetime
import http
import json
from textwrap import dedent
import time
from typing import Sequence, cast

import clickhouse_connect
from eave.core.internal.clickhouse import clickhouse_client
from eave.core.internal.clickhouse.dbchanges import DatabaseChangesTableHandle
from eave.core.internal.config import CORE_API_APP_CONFIG
from eave.core.internal.orm.client_credentials import ClientCredentialsOrm, ClientScope
from eave.monitoring.datastructures import DataIngestRequestBody, DatabaseChangeEventPayload, DatabaseChangeOperation, EventType, RawEvent
from eave.stdlib.headers import EAVE_CLIENT_ID, EAVE_CLIENT_SECRET
from .base import BaseTestCase

chclient = clickhouse_connect.get_client(host=CORE_API_APP_CONFIG.clickhouse_host)

class TestDataIngestionEndpoint(BaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

        async with self.db_session.begin() as s:
            self._team = await self.make_team(session=s)
            self._client_credentials = await ClientCredentialsOrm.create(
                session=s,
                team_id=self._team.id,
                description=self.anystr(),
                scopes=[ClientScope.read, ClientScope.write],
            )

        chclient.command(f"DROP DATABASE IF EXISTS {self._team.id.hex}")

    async def asyncTearDown(self) -> None:
        await super().asyncTearDown()

    def _ch_team_db_exists(self) -> bool:
        results = chclient.command("SHOW DATABASES")
        results = cast(list[str], results)
        return self._team.id.hex in results

    def _ch_table_exists(self, table_name: str) -> bool:
        results = chclient.command("SHOW TABLES")
        results = cast(list[str], results)
        return table_name in results


    async def test_ingest_invalid_credentials(self) -> None:
        response = await self.make_request(
            path="/ingest",
            headers={
                EAVE_CLIENT_ID: str(self.anyuuid("invalid client ID")),
                EAVE_CLIENT_SECRET: self.anystr("invalid client secret"),
            },
            payload=DataIngestRequestBody(
                event_type=EventType.dbchange,
                events=[]
            ).to_dict()
        )

        assert response.status_code == http.HTTPStatus.UNAUTHORIZED
        assert not self._ch_team_db_exists()

    async def test_ingest_invalid_scopes(self) -> None:
        async with self.db_session.begin() as s:
            ro_creds = await ClientCredentialsOrm.create(
                session=s,
                team_id=self._team.id,
                description=self.anystr(),
                scopes=[ClientScope.read],
            )

        response = await self.make_request(
            path="/ingest",
            headers={
                EAVE_CLIENT_ID: str(ro_creds.id),
                EAVE_CLIENT_SECRET: ro_creds.secret,
            },
            payload=DataIngestRequestBody(
                event_type=EventType.dbchange,
                events=[]
            ).to_dict()
        )

        assert response.status_code == http.HTTPStatus.FORBIDDEN
        assert not self._ch_team_db_exists()

    async def test_ingest_valid_credentials(self) -> None:
        response = await self.make_request(
            path="/ingest",
            headers={
                EAVE_CLIENT_ID: str(self._client_credentials.id),
                EAVE_CLIENT_SECRET: self._client_credentials.secret,
            },
            payload=DataIngestRequestBody(
                event_type=EventType.dbchange,
                events=[
                ]
            ).to_dict()
        )

        assert response.status_code == http.HTTPStatus.OK

    async def test_insert_with_no_events_doesnt_lazy_create_anything(self) -> None:
        assert not self._ch_team_db_exists()

        response = await self.make_request(
            path="/ingest",
            headers={
                EAVE_CLIENT_ID: str(self._client_credentials.id),
                EAVE_CLIENT_SECRET: self._client_credentials.secret,
            },
            payload=DataIngestRequestBody(
                event_type=EventType.dbchange,
                events=[]
            ).to_dict()
        )

        assert response.status_code == http.HTTPStatus.OK
        assert not self._ch_team_db_exists()

    async def test_insert_with_events_lazy_creates_db_and_tables(self) -> None:
        assert not self._ch_team_db_exists()
        assert not self._ch_table_exists("dbchanges")

        response = await self.make_request(
            path="/ingest",
            headers={
                EAVE_CLIENT_ID: str(self._client_credentials.id),
                EAVE_CLIENT_SECRET: self._client_credentials.secret,
            },
            payload=DataIngestRequestBody(
                event_type=EventType.dbchange,
                events=[
                    DatabaseChangeEventPayload(
                        operation=DatabaseChangeOperation.INSERT,
                        table_name=self.anystr(),
                        timestamp=int(time.time()),
                        new_data={
                            self.anystr("new_data_1"): self.anystr(),
                            self.anystr("new_data_2"): self.anystr(),
                        },
                        old_data=None,
                    ).to_json(),
                ],
            ).to_dict()
        )

        assert response.status_code == http.HTTPStatus.OK
        assert self._ch_team_db_exists()
        assert self._ch_table_exists("dbchanges")
