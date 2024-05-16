import time
from typing import Any, override

from google.cloud.bigquery import SchemaField, StandardSqlTypeNames

from eave.collectors.core.datastructures import (
    BrowserEventPayload,
)

from .table_handle import BigQueryFieldMode, BigQueryTableDefinition, BigQueryTableHandle


class BrowserEventsTableHandle(BigQueryTableHandle):
    table_def = BigQueryTableDefinition(
        table_id="atoms_browser_events",
        schema=[
            SchemaField(
                name="action_name",
                field_type=StandardSqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SchemaField(
                name="idsite",
                field_type=StandardSqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SchemaField(
                name="h",
                field_type=StandardSqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SchemaField(
                name="m",
                field_type=StandardSqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SchemaField(
                name="s",
                field_type=StandardSqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SchemaField(
                name="e_a",
                field_type=StandardSqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SchemaField(
                name="e_c",
                field_type=StandardSqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SchemaField(
                name="e_n",
                field_type=StandardSqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SchemaField(
                name="e_v",
                field_type=StandardSqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SchemaField(
                name="e_ts",
                field_type=StandardSqlTypeNames.TIMESTAMP,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SchemaField(
                name="url",
                field_type=StandardSqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SchemaField(
                name="queryParams",
                field_type=StandardSqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SchemaField(
                name="_eave_visitor_id",
                field_type=StandardSqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SchemaField(
                name="_eave_session_id",
                field_type=StandardSqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SchemaField(
                name="pv_id",
                field_type=StandardSqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SchemaField(
                name="pf_net",
                field_type=StandardSqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SchemaField(
                name="pf_srv",
                field_type=StandardSqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SchemaField(
                name="pf_tfr",
                field_type=StandardSqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SchemaField(
                name="pf_dm1",
                field_type=StandardSqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SchemaField(
                name="eaveClientId",
                field_type=StandardSqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SchemaField(
                name="uadata",
                field_type=StandardSqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SchemaField(
                name="pdf",
                field_type=StandardSqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SchemaField(
                name="qt",
                field_type=StandardSqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SchemaField(
                name="realp",
                field_type=StandardSqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SchemaField(
                name="wma",
                field_type=StandardSqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SchemaField(
                name="fla",
                field_type=StandardSqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SchemaField(
                name="java",
                field_type=StandardSqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SchemaField(
                name="ag",
                field_type=StandardSqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SchemaField(
                name="cookie",
                field_type=StandardSqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SchemaField(
                name="res",
                field_type=StandardSqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SchemaField(
                name="_extra",
                field_type=StandardSqlTypeNames.JSON,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SchemaField(
                name="timestamp",
                field_type=StandardSqlTypeNames.TIMESTAMP,
                mode=BigQueryFieldMode.NULLABLE,
            ),
        ],
    )

    async def create_vevent_view(self, *, request_method: str, request_url: str) -> None:
        pass
        # vevent_readable_name = make_virtual_event_readable_name(operation=operation, table_name=source_table)
        # vevent_view_id = "events_{event_name}".format(
        #     event_name=tableize(vevent_readable_name),
        # )

        # async with database.async_session.begin() as db_session:
        #     vevent_query = await VirtualEventOrm.query(
        #         session=db_session,
        #         params=VirtualEventOrm.QueryParams(
        #             team_id=self.team.id,
        #             view_id=vevent_view_id,
        #         ),
        #     )

        #     if not vevent_query.one_or_none():
        #         self._bq_client.get_or_create_view(
        #             dataset_id=self.team.bq_dataset_id,
        #             view_id=vevent_view_id,
        #             view_query=dedent(
        #                 """
        #                 SELECT
        #                     *
        #                 FROM
        #                     {dataset_id}.{atom_table_id}
        #                 WHERE
        #                     `table_name` = {source_table}
        #                     AND `operation` = {operation}
        #                 ORDER BY
        #                     `timestamp` ASC
        #                 """.format(
        #                     dataset_id=sql_sanitized_identifier(self.team.bq_dataset_id),
        #                     atom_table_id=sql_sanitized_identifier(self.table_def.table_id),
        #                     source_table=sql_sanitized_literal(source_table),
        #                     operation=sql_sanitized_literal(operation),
        #                 )
        #             ).strip(),
        #         )

        #         await VirtualEventOrm.create(
        #             session=db_session,
        #             team_id=self.team.id,
        #             view_id=vevent_view_id,
        #             readable_name=vevent_readable_name,
        #             description=f"{operation} operation on the {source_table} table.",
        #         )

    @override
    async def insert(self, events: list[dict[str, Any]]) -> None:
        if len(events) == 0:
            return

        browser_events = [BrowserEventPayload(**e) for e in events]

        dataset = self._bq_client.get_or_create_dataset(
            dataset_id=self.team.bq_dataset_id,
        )

        table = self._bq_client.get_and_sync_or_create_table(
            dataset_id=dataset.dataset_id,
            table_id=self.table_def.table_id,
            schema=self.table_def.schema,
        )

        unique_operations: set[tuple[str, str]] = set()
        formatted_rows: list[dict[str, Any]] = []

        for e in browser_events:
            # unique_operations.add((e.request_method, e.request_url))
            formatted_rows.append({
                "timestamp": time.time(),
                **e.to_dict(),
            })

        self._bq_client.append_rows(
            table=table,
            rows=formatted_rows,
        )

        # FIXME: This is vulnerable to a DoS
        for request_method, request_url in unique_operations:
            await self.create_vevent_view(request_method=request_method, request_url=request_url)
