import time
from textwrap import dedent
from typing import Any, cast, override

from eave.stdlib.typing import JsonObject
from google.cloud.bigquery import SchemaField, StandardSqlTypeNames

from eave.collectors.core.datastructures import DatabaseEventPayload, DatabaseOperation
from eave.core.internal import database
from eave.core.internal.atoms.shared import discovery_field, insert_timestamp_field, key_value_record_field, session_field, timestamp_field, user_field
from eave.core.internal.orm.virtual_event import VirtualEventOrm
from eave.stdlib.logging import LOGGER, LogContext
from eave.stdlib.util import sql_sanitized_identifier, sql_sanitized_literal, tableize, titleize

from .table_handle import BigQueryFieldMode, BigQueryTableDefinition, BigQueryTableHandle


class DatabaseEventsTableHandle(BigQueryTableHandle):
    table_def = BigQueryTableDefinition(
        table_id="atoms_db_events_v1",
        description="Database atoms",
        schema=(
            SchemaField(
                name="operation",
                description="Which operation (SQL verb) was performed.",
                field_type=StandardSqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),

            SchemaField(
                name="db_name",
                description="The name of the database.",
                field_type=StandardSqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SchemaField(
                name="table_name",
                description="The name of the table.",
                field_type=StandardSqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),

            timestamp_field(),
            session_field(),
            user_field(),
            discovery_field(),

            SchemaField(
                name="statement",
                description="The full database statement.",
                field_type=StandardSqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),

            key_value_record_field(name="parameters", description="The SQL parameters passed into the statement."),

            insert_timestamp_field(),
        ),
    )

    @override
    async def insert(self, events: list[JsonObject], ctx: LogContext) -> None:
        if len(events) == 0:
            return

        db_events = [DatabaseEventPayload(**e) for e in events]

        dataset = self._bq_client.get_or_create_dataset(
            dataset_id=self.team.bq_dataset_id,
        )

        table = self._bq_client.get_and_sync_or_create_table(
            dataset_id=dataset.dataset_id,
            table_id=self.table_def.table_id,
            schema=self.table_def.schema,
            description=self.table_def.description,
            ctx=ctx,
        )

        unique_operations: set[tuple[str, str]] = set()
        formatted_rows: list[dict[str, Any]] = []
        insert_timestamp = time.time()

        for e in db_events:
            if not e.operation or not e.table_name:
                LOGGER.warning("Missing parameters e.operation and/or e.table_name", ctx)
                continue

            unique_operations.add((e.operation, e.table_name))
            row = e.to_dict()
            row["insert_timestamp"] = insert_timestamp
            formatted_rows.append(row)

        errors = self._bq_client.append_rows(
            table=table,
            rows=formatted_rows,
        )

        if len(errors) > 0:
            LOGGER.warning("BigQuery insert errors", {"errors": cast(list, errors)}, ctx)

        # FIXME: This is vulnerable to a DoS where unique `table_name` is generated and inserted on a loop.
        for operation, table_name in unique_operations:
            await self.create_or_update_vevent_view(sanitized_operation=operation, sanitized_source_table=table_name, ctx=ctx)

    async def create_or_update_vevent_view(self, *, sanitized_operation: str, sanitized_source_table: str, ctx: LogContext) -> None:
        table_resource = titleize(sanitized_source_table)
        operation_verb = _operation_readable_verb_past_tense(sanitized_operation)
        vevent_readable_name = f"{operation_verb} {table_resource}"
        vevent_view_id = tableize(vevent_readable_name)

        async with database.async_session.begin() as db_session:
            vevent_query = (await VirtualEventOrm.query(
                session=db_session,
                params=VirtualEventOrm.QueryParams(
                    team_id=self.team.id,
                    view_id=vevent_view_id,
                ),
            )).one_or_none()

            try:
                sanitized_dataset_id = sql_sanitized_identifier(self.team.bq_dataset_id)
                sanitized_atom_table_id = sql_sanitized_identifier(self.table_def.table_id)
                sanitized_source_table = sql_sanitized_literal(sanitized_source_table)
                sanitized_operation = sql_sanitized_literal(sanitized_operation)

                self._bq_client.get_and_sync_or_create_view(
                    dataset_id=self.team.bq_dataset_id,
                    view_id=vevent_view_id,
                    description=vevent_readable_name,
                    mview_query=dedent(
                        f"""
                        SELECT
                            {vevent_readable_name} as event_name,
                            (SELECT context.value FROM
                            JSON_VALUE(context, "$.user_id") as user_id,
                            table_name,
                            operation,
                            timestamp,
                        FROM
                            {sanitized_dataset_id}.{sanitized_atom_table_id}
                        WHERE
                            `table_name` = {sanitized_source_table}
                            AND `operation` = {sanitized_operation}
                        ORDER BY
                            `timestamp` ASC
                        """
                    ).strip(),
                )

                await VirtualEventOrm.create(
                    session=db_session,
                    team_id=self.team.id,
                    view_id=vevent_view_id,
                    readable_name=vevent_readable_name,
                    description=f"{sanitized_operation} operation on the {sanitized_source_table} table.",
                )
            except Exception as e:
                # This may indicate a race condition, where two requests attempted to create the same view/virtual event at the same time.
                # In that case, it's okay to ignore the failure.
                LOGGER.exception(e, ctx)

def _operation_readable_verb_past_tense(operation: str) -> str:
    db_operation = DatabaseOperation.from_str(operation)
    match db_operation:
        case DatabaseOperation.INSERT:
            return "Created"
        case DatabaseOperation.UPDATE:
            return "Updated"
        case DatabaseOperation.DELETE:
            return "Deleted"
        case DatabaseOperation.SELECT:
            return "Queried"
        case _:
            # TODO: What verb to use for an invalid DatabaseOperation value?
            return "Inspected"
