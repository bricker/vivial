from textwrap import dedent
from typing import Any, cast, override

from google.cloud.bigquery import SchemaField, StandardSqlTypeNames

from eave.collectors.core.datastructures import DatabaseEventPayload, DatabaseStructure
from eave.core.internal import database
from eave.core.internal.orm.virtual_event import VirtualEventOrm, make_virtual_event_readable_name
from eave.stdlib.logging import LOGGER
from eave.stdlib.util import sql_sanitized_identifier, sql_sanitized_literal, tableize

from .table_handle import BigQueryFieldMode, BigQueryTableDefinition, BigQueryTableHandle


class DatabaseEventsTableHandle(BigQueryTableHandle):
    table_def = BigQueryTableDefinition(
        table_id="atoms_db",
        schema=[
            SchemaField(
                name="statement",
                field_type=StandardSqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SchemaField(
                name="db_structure",
                field_type=StandardSqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SchemaField(
                name="db_name",
                field_type=StandardSqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SchemaField(
                name="table_name",
                field_type=StandardSqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SchemaField(
                name="operation",
                field_type=StandardSqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SchemaField(
                name="timestamp",
                field_type=StandardSqlTypeNames.TIMESTAMP,
                mode=BigQueryFieldMode.REQUIRED,
            ),
            SchemaField(
                name="parameters",
                field_type=StandardSqlTypeNames.JSON,
                mode=BigQueryFieldMode.NULLABLE,
            ),
        ],
    )

    async def create_vevent_view(self, *, operation: str, source_table: str) -> None:
        vevent_readable_name = make_virtual_event_readable_name(operation=operation, table_name=source_table)
        vevent_view_id = "events_{event_name}".format(
            event_name=tableize(vevent_readable_name),
        )

        async with database.async_session.begin() as db_session:
            vevent_query = await VirtualEventOrm.query(
                session=db_session,
                params=VirtualEventOrm.QueryParams(
                    team_id=self.team.id,
                    view_id=vevent_view_id,
                ),
            )

            if not vevent_query.one_or_none():
                try:
                    self._bq_client.get_or_create_view(
                        dataset_id=self.team.bq_dataset_id,
                        view_id=vevent_view_id,
                        view_query=dedent(
                            """
                            SELECT
                                *
                            FROM
                                {dataset_id}.{atom_table_id}
                            WHERE
                                `table_name` = {source_table}
                                AND `operation` = {operation}
                            ORDER BY
                                `timestamp` ASC
                            """.format(
                                dataset_id=sql_sanitized_identifier(self.team.bq_dataset_id),
                                atom_table_id=sql_sanitized_identifier(self.table_def.table_id),
                                source_table=sql_sanitized_literal(source_table),
                                operation=sql_sanitized_literal(operation),
                            )
                        ).strip(),
                    )

                    await VirtualEventOrm.create(
                        session=db_session,
                        team_id=self.team.id,
                        view_id=vevent_view_id,
                        readable_name=vevent_readable_name,
                        description=f"{operation} operation on the {source_table} table.",
                    )
                except Exception as e:
                    # This may indicate a race condition, where two requests attempted to create the same view/virtual event at the same time.
                    # In that case, it's okay to ignore the failure.
                    LOGGER.exception(e)

    @override
    async def insert(self, events: list[dict[str, Any]]) -> None:
        if len(events) == 0:
            return

        db_events = [DatabaseEventPayload(**e) for e in events]

        dataset = self._bq_client.get_or_create_dataset(
            dataset_id=self.team.bq_dataset_id,
        )

        table = self._bq_client.get_or_create_table(
            dataset_id=dataset.dataset_id,
            table_id=self.table_def.table_id,
            schema=self.table_def.schema,
        )

        unique_operations: set[tuple[str, str]] = set()
        formatted_rows: list[dict[str, Any]] = []

        for e in db_events:
            match e.db_structure:
                case DatabaseStructure.SQL:
                    if not e.operation or not e.table_name:
                        LOGGER.warning("Missing parameters e.operation and/or e.table_name")
                        continue

                    unique_operations.add((e.operation, e.table_name))
                    formatted_rows.append(e.to_dict())
                case _:
                    # TODO: handle noSQL
                    raise NotImplementedError("noSQL not implemented")

        LOGGER.debug(
            "inserting records", {"table": table.table_id, "dataset": table.dataset_id, "rows": formatted_rows}
        )

        result = self._bq_client.append_rows(
            table=table,
            rows=formatted_rows,
        )

        result = cast(list[dict[str, Any]], result)
        LOGGER.debug("insert results", {"table": table.table_id, "dataset": table.dataset_id, "result": result})

        # FIXME: This is vulnerable to a DoS where unique `table_name` is generated and inserted on a loop.
        for operation, table_name in unique_operations:
            await self.create_vevent_view(operation=operation, source_table=table_name)
