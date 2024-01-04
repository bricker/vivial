from datetime import datetime
import json
from textwrap import dedent

import clickhouse_connect
from eave.core.internal.clickhouse import clickhouse_client
from eave.core.internal.clickhouse.dbchanges import DatabaseChangesTableHandle
from eave.core.internal.config import CORE_API_APP_CONFIG
from eave.monitoring.datastructures import DatabaseChangeEventPayload, EventType, RawEvent
from .base import BaseTestCase

chclient = clickhouse_connect.get_client(host=CORE_API_APP_CONFIG.clickhouse_host)

class TestClickhouseIntegration(BaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

        async with self.db_session.begin() as s:
            self._team = await self.make_team(session=s)

        self._table_handle = DatabaseChangesTableHandle(team_id=self._team.id)
        chclient.command(f"DROP DATABASE IF EXISTS {self._table_handle.database}")

    async def asyncTearDown(self) -> None:
        await super().asyncTearDown()

    # async def test_insert(self) -> None:
    #     ts = datetime.now().isoformat()
    #     query = dedent(f"""
    #         SELECT
    #             *
    #         FROM
    #             {self._table_handle.database}.{self._table_handle.table.name}
    #         WHERE
    #             table_name='accounts'
    #             AND operation='INSERT'
    #             AND timestamp='{ts}'
    #         """).strip()

    #     await self._table_handle.insert(events=[
    #         RawEvent(
    #             event_type=EventType.dbchange,
    #             payload=json.dumps(DatabaseChangeEventPayload(
    #                 table_name="accounts",
    #                 operation="INSERT",
    #                 timestamp=ts,
    #                 new_data=None,
    #                 old_data=None,
    #             ).to_dict())
    #         )
    #     ])

    #     results = await self._table_handle.query(query)
    #     assert results.row_count == 1

    #     results = await self._table_handle.query(
    #         dedent(f"""
    #             SELECT
    #                 *
    #             FROM
    #                 {self._table_handle.database}.account_created_events
    #             """
    #         ).strip()
    #     )
    #     assert results.row_count == 1