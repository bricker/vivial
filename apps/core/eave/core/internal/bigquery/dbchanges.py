import json
import re
from textwrap import dedent
from typing import override
from google.cloud.bigquery import SchemaField, StandardSqlTypeNames
from google.cloud.bigquery.table import RowIterator

from eave.core.internal.bigquery.types import BigQueryFieldMode, BigQueryTableDefinition, BigQueryTableHandle
from eave.core.internal.orm.virtual_event import VirtualEventOrm, make_virtual_event_readable_name
from eave.monitoring.datastructures import DatabaseChangeEventPayload, DatabaseChangeOperation
from eave.core.internal import database
from eave.core.internal.bigquery import bq_client
from eave.stdlib.util import sql_sanitized_identifier, sql_sanitized_literal, tableize

table_definition = BigQueryTableDefinition(
    name="dbchanges",
    schema=[
        SchemaField(
            name="table_name",
            description="The name of the table that was modified",
            field_type=StandardSqlTypeNames.STRING,
            mode=BigQueryFieldMode.REQUIRED,
        ),
        SchemaField(
            name="operation",
            description="The table operation (INSERT, UPDATE, or DELETE)",
            field_type=StandardSqlTypeNames.STRING,
            mode=BigQueryFieldMode.REQUIRED,
        ),
        SchemaField(
            name="timestamp",
            description="The timestamp of the table operation",
            field_type=StandardSqlTypeNames.TIMESTAMP,
            mode=BigQueryFieldMode.REQUIRED,
        ),
        SchemaField(
            name="old_data",
            description="The row data before the change (will be NULL for INSERTs)",
            field_type=StandardSqlTypeNames.JSON,
            mode=BigQueryFieldMode.NULLABLE,
        ),
        SchemaField(
            name="new_data",
            description="The row data after the change (will be NULL for DELETEs)",
            field_type=StandardSqlTypeNames.JSON,
            mode=BigQueryFieldMode.NULLABLE,
        ),
    ],
)


class DatabaseChangesTableHandle(BigQueryTableHandle):
    table = table_definition

    async def create_vevent_view(self, *, operation: str, source_table: str) -> None:
        vevent_readable_name = make_virtual_event_readable_name(operation=operation, table_name=source_table)
        vevent_view_name = tableize(vevent_readable_name)

        async with database.async_session.begin() as db_session:
            vevent_query = await VirtualEventOrm.query(
                session=db_session,
                params=VirtualEventOrm.QueryParams(
                    team_id=self.team_id,
                    view_name=vevent_view_name,
                )
            )

            if not vevent_query.one_or_none():
                bq_client.create_view(
                    dataset_name=self.dataset_name,
                    view_name=vevent_view_name,
                    view_query=dedent(
                        """
                        SELECT
                            *
                        FROM
                            {dataset}.{atom_table_name}
                        WHERE
                            `table_name` = {source_table}
                            AND `operation` = {operation}
                        ORDER BY
                            `timestamp` ASC
                        """.format(
                            dataset=sql_sanitized_identifier(self.dataset_name),
                            atom_table_name=sql_sanitized_identifier(self.table.name),
                            source_table=sql_sanitized_literal(source_table),
                            operation=sql_sanitized_literal(operation),
                        )
                    ).strip(),
                )

                await VirtualEventOrm.create(
                    session=db_session,
                    team_id=self.team_id,
                    view_name=vevent_view_name,
                    readable_name=vevent_readable_name,
                    description=f"{operation} operation on the {source_table} table.",
                )



    @override
    async def insert(self, events: list[str]) -> None:
        if len(events) == 0:
            return

        dbchange_events = [DatabaseChangeEventPayload(**json.loads(e)) for e in events]

        bq_client.create_dataset(dataset_name=self.dataset_name)
        bq_client.create_table(
            dataset_name=self.dataset_name,
            table_name=self.table.name,
            schema=self.table.schema,
        )

        bq_client.append_rows(
            dataset_name=self.dataset_name,
            table_name=self.table.name,
            schema=self.table.schema,
            rows=[e.to_dict() for e in dbchange_events],
        )

        unique_operations = set((e.operation, e.table_name) for e in dbchange_events)

        # FIXME: This is vulnerable to a DoS where unique `table_name` is generated and inserted on a loop.
        for operation, table_name in unique_operations:
            await self.create_vevent_view(operation=operation, source_table=table_name)

    @override
    async def query(self, query: str) -> RowIterator:
        results = bq_client.query(query=query)
        return results

    # def _format_row(self, event: DatabaseChangeEventPayload) -> list[Any]:
    #     """
    #     >>> _format_row(event=RawEvent(event_type="dbchange", payload='{"timestamp":"2023-12-22T17:09:22.797036", "table_name":"accounts", "operation":"INSERT", "new_data":"_new", "old_data":"_old"}'))
    #     {'table_name': 'accounts', 'operation': 'INSERT', 'timestamp': '2023-12-22T17:09:22.797036', 'new_data': {'accounts': '_new'}, 'old_data': {'accounts': '_old'}}
    #     """
    #     d = {
    #         "table_name": event.table_name,
    #         "operation": event.operation,
    #         "timestamp": datetime.fromtimestamp(event.timestamp),
    #         "new_data": {event.table_name: event.new_data},
    #         "old_data": {event.table_name: event.old_data},
    #     }

    #     # This effectively puts the values in the right order.
    #     return [d[c.name] for c in self.table.columns]
