from dataclasses import dataclass
import dataclasses
from datetime import datetime
import json
from textwrap import dedent
from typing import Any, Optional, override
from google.cloud.bigquery import SchemaField, StandardSqlTypeNames

from eave.core.internal.bigquery.types import BigQueryFieldMode, BigQueryTableDefinition, BigQueryTableHandle
from eave.core.internal.orm.virtual_event import VirtualEventOrm, make_virtual_event_readable_name
from eave.tracing.core.datastructures import DatabaseChangeEventPayload
from eave.core.internal import database
from eave.stdlib.util import sql_sanitized_identifier, sql_sanitized_literal, tableize


@dataclass(frozen=True)
class _DatabaseChangesTableSchema:
    """
    Convenience class for typing input data.
    The associated BigQueryTableDefinition is authoritative.
    """

    table_name: str
    operation: str
    timestamp: datetime
    old_data: Optional[dict[str, Any]]
    new_data: Optional[dict[str, Any]]


class DatabaseChangesTableHandle(BigQueryTableHandle):
    table_def = BigQueryTableDefinition(
        table_id="atoms_dbchanges",
        schema=[
            SchemaField(
                name="table_name",
                field_type=StandardSqlTypeNames.STRING,
                mode=BigQueryFieldMode.REQUIRED,
            ),
            SchemaField(
                name="operation",
                field_type=StandardSqlTypeNames.STRING,
                mode=BigQueryFieldMode.REQUIRED,
            ),
            SchemaField(
                name="timestamp",
                field_type=StandardSqlTypeNames.TIMESTAMP,
                mode=BigQueryFieldMode.REQUIRED,
            ),
            SchemaField(
                name="old_data",
                field_type=StandardSqlTypeNames.JSON,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SchemaField(
                name="new_data",
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
                    team_id=self.team_id,
                    view_id=vevent_view_id,
                ),
            )

            if not vevent_query.one_or_none():
                self._bq_client.get_or_create_view(
                    dataset_id=self.dataset_id,
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
                            dataset_id=sql_sanitized_identifier(self.dataset_id),
                            atom_table_id=sql_sanitized_identifier(self.table_def.table_id),
                            source_table=sql_sanitized_literal(source_table),
                            operation=sql_sanitized_literal(operation),
                        )
                    ).strip(),
                )

                await VirtualEventOrm.create(
                    session=db_session,
                    team_id=self.team_id,
                    view_id=vevent_view_id,
                    readable_name=vevent_readable_name,
                    description=f"{operation} operation on the {source_table} table.",
                )

    @override
    async def insert(self, events: list[str]) -> None:
        if len(events) == 0:
            return

        dbchange_events = [DatabaseChangeEventPayload(**json.loads(e)) for e in events]

        dataset = self._bq_client.get_or_create_dataset(
            dataset_id=self.dataset_id,
        )

        table = self._bq_client.get_or_create_table(
            dataset_id=dataset.dataset_id,
            table_id=self.table_def.table_id,
            schema=self.table_def.schema,
        )

        self._bq_client.append_rows(
            table=table,
            rows=[self._format_row(e) for e in dbchange_events],
        )

        unique_operations = {(e.operation, e.table_name) for e in dbchange_events}

        # FIXME: This is vulnerable to a DoS where unique `table_name` is generated and inserted on a loop.
        for operation, table_name in unique_operations:
            await self.create_vevent_view(operation=operation, source_table=table_name)

    def _format_row(self, event: DatabaseChangeEventPayload) -> dict[str, Any]:
        d = _DatabaseChangesTableSchema(
            table_name=event.table_name,
            operation=event.operation,
            timestamp=datetime.fromtimestamp(event.timestamp),
            new_data=event.new_data,
            old_data=event.old_data,
        )
        return dataclasses.asdict(d)
