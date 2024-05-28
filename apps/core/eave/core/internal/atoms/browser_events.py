import math
import time
from typing import Any, cast, override

from eave.stdlib.logging import LOGGER, LogContext
from eave.stdlib.typing import JsonObject
from google.cloud.bigquery import SchemaField, SqlTypeNames, StandardSqlTypeNames

from .table_handle import BigQueryFieldMode, BigQueryTableDefinition, BigQueryTableHandle

class BrowserEventsTableHandle(BigQueryTableHandle):
    table_def = BigQueryTableDefinition(
        table_id="atoms_browser_events_v1",
        schema=(
            SchemaField(
                name="event",
                field_type=SqlTypeNames.RECORD,
                mode=BigQueryFieldMode.NULLABLE,
                fields=(
                     SchemaField(
                        name="action",
                        field_type=SqlTypeNames.STRING,
                        mode=BigQueryFieldMode.NULLABLE,
                    ),
                    SchemaField(
                        name="timestamp",
                        field_type=SqlTypeNames.TIMESTAMP,
                        mode=BigQueryFieldMode.NULLABLE,
                    ),
                    SchemaField(
                        name="origin_elapsed_ms",
                        field_type=SqlTypeNames.FLOAT,
                        mode=BigQueryFieldMode.NULLABLE,
                    ),
                    SchemaField(
                        name="target",
                        field_type=SqlTypeNames.RECORD,
                        mode=BigQueryFieldMode.NULLABLE,
                        fields=(
                            SchemaField(
                                name="type",
                                field_type=SqlTypeNames.STRING,
                                mode=BigQueryFieldMode.NULLABLE,
                            ),
                            SchemaField(
                                name="id",
                                field_type=SqlTypeNames.STRING,
                                mode=BigQueryFieldMode.NULLABLE,
                            ),
                            SchemaField(
                                name="text",
                                field_type=SqlTypeNames.STRING,
                                mode=BigQueryFieldMode.NULLABLE,
                            ),
                            SchemaField(
                                name="attributes",
                                field_type=StandardSqlTypeNames.JSON,
                                mode=BigQueryFieldMode.NULLABLE,
                            ),
                        ),
                    ),
                ),
            ),

            SchemaField(
                name="session",
                field_type=SqlTypeNames.RECORD,
                mode=BigQueryFieldMode.NULLABLE,
                fields=(
                    SchemaField(
                        name="id",
                        field_type=SqlTypeNames.STRING,
                        mode=BigQueryFieldMode.NULLABLE,
                    ),
                    SchemaField(
                        name="start_timestamp",
                        field_type=SqlTypeNames.TIMESTAMP,
                        mode=BigQueryFieldMode.NULLABLE,
                    ),
                    SchemaField(
                        name="duration_ms",
                        field_type=SqlTypeNames.INTEGER,
                        mode=BigQueryFieldMode.NULLABLE,
                    ),
                ),
            ),

            SchemaField(
                name="user",
                field_type=SqlTypeNames.RECORD,
                mode=BigQueryFieldMode.NULLABLE,
                fields=(
                    SchemaField(
                        name="id",
                        field_type=SqlTypeNames.STRING,
                        mode=BigQueryFieldMode.NULLABLE,
                    ),
                    SchemaField(
                        name="visitor_id",
                        field_type=SqlTypeNames.STRING,
                        mode=BigQueryFieldMode.NULLABLE,
                    ),
                ),
            ),


            SchemaField(
                name="page",
                field_type=SqlTypeNames.RECORD,
                mode=BigQueryFieldMode.NULLABLE,
                fields=(
                    SchemaField(
                        name="current_url",
                        field_type=SqlTypeNames.STRING,
                        mode=BigQueryFieldMode.NULLABLE,
                    ),
                    SchemaField(
                        name="current_title",
                        field_type=SqlTypeNames.STRING,
                        mode=BigQueryFieldMode.NULLABLE,
                    ),
                    SchemaField(
                        name="pageview_id",
                        field_type=SqlTypeNames.STRING,
                        mode=BigQueryFieldMode.NULLABLE,
                    ),
                    SchemaField(
                        name="current_query_params",
                        field_type=StandardSqlTypeNames.JSON,
                        mode=BigQueryFieldMode.NULLABLE,
                    ),
                ),
            ),

            SchemaField(
                name="ua",
                field_type=SqlTypeNames.RECORD,
                mode=BigQueryFieldMode.NULLABLE,
                fields=(
                    SchemaField(
                        name="ua_string",
                        field_type=SqlTypeNames.STRING,
                        mode=BigQueryFieldMode.NULLABLE,
                    ),
                    SchemaField(
                        name="brands",
                        field_type=SqlTypeNames.RECORD,
                        mode=BigQueryFieldMode.REPEATED,
                        fields=(
                            SchemaField(
                                name="brand",
                                field_type=SqlTypeNames.STRING,
                                mode=BigQueryFieldMode.NULLABLE,
                            ),
                            SchemaField(
                                name="version",
                                field_type=SqlTypeNames.STRING,
                                mode=BigQueryFieldMode.NULLABLE,
                            ),
                        ),
                    ),
                    SchemaField(
                        name="platform",
                        field_type=SqlTypeNames.STRING,
                        mode=BigQueryFieldMode.NULLABLE,
                    ),
                    SchemaField(
                        name="mobile",
                        field_type=SqlTypeNames.BOOLEAN,
                        mode=BigQueryFieldMode.NULLABLE,
                    ),
                    SchemaField(
                        name="form_factor",
                        field_type=SqlTypeNames.STRING,
                        mode=BigQueryFieldMode.NULLABLE,
                    ),
                    SchemaField(
                        name="full_version_list",
                        field_type=SqlTypeNames.RECORD,
                        mode=BigQueryFieldMode.REPEATED,
                        fields=(
                            SchemaField(
                                name="brand",
                                field_type=SqlTypeNames.STRING,
                                mode=BigQueryFieldMode.NULLABLE,
                            ),
                            SchemaField(
                                name="version",
                                field_type=SqlTypeNames.STRING,
                                mode=BigQueryFieldMode.NULLABLE,
                            ),
                        ),
                    ),
                    SchemaField(
                        name="model",
                        field_type=SqlTypeNames.STRING,
                        mode=BigQueryFieldMode.NULLABLE,
                    ),
                    SchemaField(
                        name="platform_version",
                        field_type=SqlTypeNames.STRING,
                        mode=BigQueryFieldMode.NULLABLE,
                    ),
                ),
            ),

            SchemaField(
                name="discovery",
                field_type=SqlTypeNames.RECORD,
                mode=BigQueryFieldMode.NULLABLE,
                fields=(
                    SchemaField(
                        name="timestamp",
                        field_type=SqlTypeNames.TIMESTAMP,
                        mode=BigQueryFieldMode.NULLABLE,
                    ),
                    SchemaField(
                        name="browser_referrer",
                        field_type=SqlTypeNames.STRING,
                        mode=BigQueryFieldMode.NULLABLE,
                    ),
                    SchemaField(
                        name="campaign",
                        field_type=SqlTypeNames.STRING,
                        mode=BigQueryFieldMode.NULLABLE,
                    ),
                    SchemaField(
                        name="gclid",
                        field_type=SqlTypeNames.STRING,
                        mode=BigQueryFieldMode.NULLABLE,
                    ),
                    SchemaField(
                        name="fbclid",
                        field_type=SqlTypeNames.STRING,
                        mode=BigQueryFieldMode.NULLABLE,
                    ),
                    SchemaField(
                        name="utm_params",
                        field_type=StandardSqlTypeNames.JSON,
                        mode=BigQueryFieldMode.NULLABLE,
                    ),
                ),
            ),

            SchemaField(
                name="screen",
                field_type=SqlTypeNames.RECORD,
                mode=BigQueryFieldMode.NULLABLE,
                fields=(
                    SchemaField(
                        name="width",
                        field_type=SqlTypeNames.INTEGER,
                        mode=BigQueryFieldMode.NULLABLE,
                    ),
                    SchemaField(
                        name="height",
                        field_type=SqlTypeNames.INTEGER,
                        mode=BigQueryFieldMode.NULLABLE,
                    ),
                    SchemaField(
                        name="avail_width",
                        field_type=SqlTypeNames.INTEGER,
                        mode=BigQueryFieldMode.NULLABLE,
                    ),
                    SchemaField(
                        name="avail_height",
                        field_type=SqlTypeNames.INTEGER,
                        mode=BigQueryFieldMode.NULLABLE,
                    ),
                ),
            ),

            SchemaField(
                name="perf",
                field_type=SqlTypeNames.RECORD,
                mode=BigQueryFieldMode.NULLABLE,
                fields=(
                    SchemaField(
                        name="network_latency_ms",
                        field_type=SqlTypeNames.FLOAT,
                        mode=BigQueryFieldMode.NULLABLE,
                    ),
                    SchemaField(
                        name="dom_load_latency_ms",
                        field_type=SqlTypeNames.FLOAT,
                        mode=BigQueryFieldMode.NULLABLE,
                    ),
                ),
            ),

            SchemaField(
                name="cookies",
                field_type=StandardSqlTypeNames.JSON,
                mode=BigQueryFieldMode.NULLABLE,
            ),

            SchemaField(
                name="extra",
                field_type=StandardSqlTypeNames.JSON,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SchemaField(
                name="client_ip",
                field_type=SqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SchemaField(
                name="context",
                field_type=StandardSqlTypeNames.JSON,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SchemaField(
                name="insert_timestamp",
                field_type=SqlTypeNames.TIMESTAMP,
                mode=BigQueryFieldMode.REQUIRED,
                default_value_expression="CURRENT_TIMESTAMP"
            ),
        ),
    )

    async def create_vevent_view(self, *, request_method: str, request_url: str, ctx: LogContext) -> None:
        pass
        # vevent_readable_name = make_virtual_event_readable_name(operation=operation, table_name=source_table)
        # vevent_view_id = tableize(vevent_readable_name)

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

    async def insert(self, events: list[dict[str, Any]], ctx: LogContext) -> None:
        await self.insert_with_client_ip(events, client_ip=None, ctx=ctx)

    async def insert_with_client_ip(self, events: list[dict[str, Any]], client_ip: str | None, ctx: LogContext) -> None:
        if len(events) == 0:
            return

        dataset = self._bq_client.get_or_create_dataset(
            dataset_id=self.team.bq_dataset_id,
        )

        table = self._bq_client.get_and_sync_or_create_table(
            dataset_id=dataset.dataset_id,
            table_id=self.table_def.table_id,
            schema=self.table_def.schema,
            ctx=ctx,
        )

        unique_operations: set[tuple[str, str]] = set()
        formatted_rows: list[dict[str, Any]] = []

        for e in events:
            # unique_operations.add((e.request_method, e.request_url))
            e["client_ip"] = client_ip
            formatted_rows.append(e)

        errors = self._bq_client.append_rows(
            table=table,
            rows=formatted_rows,
        )

        if len(errors) > 0:
            LOGGER.warning("BigQuery insert errors", { "errors": cast(list, errors)}, ctx)

        # FIXME: This is vulnerable to a DoS
        for request_method, request_url in unique_operations:
            await self.create_vevent_view(request_method=request_method, request_url=request_url, ctx=ctx)
