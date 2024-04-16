import dataclasses
import json
import re
from dataclasses import dataclass
from datetime import datetime
from textwrap import dedent
from typing import Any, Optional, override

from eave.core.internal import database
from eave.core.internal.bigquery.types import BigQueryFieldMode, BigQueryTableDefinition, BigQueryTableHandle
from eave.core.internal.orm.virtual_event import VirtualEventOrm, make_virtual_event_readable_name
from eave.stdlib.util import sql_sanitized_identifier, sql_sanitized_literal, tableize
from eave.tracing.core.datastructures import DatabaseEventPayload, DatabaseOperation, DatabaseStructure
from google.cloud.bigquery import SchemaField, StandardSqlTypeNames

_leading_comment_remover = re.compile(r"^/\*.*?\*/")


@dataclass(frozen=True)
class _DatabaseChangesTableSchema:
    """
    Convenience class for typing input data.
    The associated BigQueryTableDefinition is authoritative.
    """

    table_name: str
    operation: str
    timestamp: datetime
    parameters: Optional[list[str]]

    def as_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


class DatabaseChangesTableHandle(BigQueryTableHandle):
    table_def = BigQueryTableDefinition(
        table_id="atoms_db",
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

        dbchange_events = [DatabaseEventPayload(**json.loads(e)) for e in events]

        dataset = self._bq_client.get_or_create_dataset(
            dataset_id=self.dataset_id,
        )

        table = self._bq_client.get_or_create_table(
            dataset_id=dataset.dataset_id,
            table_id=self.table_def.table_id,
            schema=self.table_def.schema,
        )

        unique_operations: set[tuple[str, str]] = set()
        formatted_rows: list[dict[str, Any]] = []

        for e in dbchange_events:
            match e.db_structure:
                case DatabaseStructure.SQL:
                    # TODO: load these vals from event now + update DatabaseEventPayload fields
                    op = _operation_name(e.statement)
                    table_name = _table_name(e.statement)
                    if not op or not table_name:
                        continue

                    unique_operations.add((op, table_name))
                    formatted_rows.append(
                        _DatabaseChangesTableSchema(
                            table_name=table_name,
                            operation=op,
                            timestamp=datetime.fromtimestamp(e.timestamp),
                            parameters=e.parameters,
                            # TODO: allo this to take the col names map, or sep list
                        ).as_dict()
                    )
                case _:
                    # TODO: handle noSQL
                    continue

        self._bq_client.append_rows(
            table=table,
            rows=formatted_rows,
        )

        # FIXME: This is vulnerable to a DoS where unique `table_name` is generated and inserted on a loop.
        for operation, table_name in unique_operations:
            await self.create_vevent_view(operation=operation, source_table=table_name)


def _operation_name(statement: str) -> str | None:
    parts = _leading_comment_remover.sub("", statement).split()
    if len(parts) == 0:
        return None
    else:
        return parts[0]


def _table_name(statement: str) -> str | None:
    table_name = None
    if isinstance(statement, str):
        parts = _leading_comment_remover.sub("", statement).replace(";", "").split()
        if len(parts) < 1:
            return None
        op_str = parts[0]
        op = DatabaseOperation.from_str(op_str)

        match op:
            case DatabaseOperation.INSERT | DatabaseOperation.DELETE:
                if len(parts) < 3:
                    return None
                table_name = parts[2]
            case DatabaseOperation.UPDATE:
                if len(parts) < 2:
                    return None
                table_name = parts[1]
            case DatabaseOperation.SELECT:
                match = re.search(r"FROM\s+([a-zA-Z0-9_\-\.]+)", statement, re.IGNORECASE)
                if match:
                    table_name = match.group(1)

    return table_name


def _columns_from_statement(statement: str) -> list[str]:
    """
    Try to extract column names from `statement` SQL (based on common sql patterns).
    Returns empty list if unable to resolve column names from the statement.

    NOTE: functionality depends heavily on values not being present in the sql `statement`; many
          edge cases related to value content arrise if values are not extracted from `statement`.
    """
    def parse_where(s: str) -> list[str]:
        """
        Parse column names from WHERE clauses in the passed in SQL statement string `s`
        """
        import sqlparse
        parsed = sqlparse.parse(s)
        if not parsed:
            return []

        where_clauses = list(filter(lambda o: isinstance(o, sqlparse.sql.Where), parsed[0].tokens))
        if len(where_clauses) < 1:
            return []

        column_names = []


        def dfs(element, cols):
            """Extracts Identifier tokens (this is what column names get typed as) from tokenized statement"""
            if isinstance(element, sqlparse.sql.IdentifierList):
                cols.extend([str(identifier) for identifier in element.get_identifiers()])
            elif isinstance(element, sqlparse.sql.Identifier):
                # make sure there arent more identifiers hiding inside
                if hasattr(element, "tokens") and len(element.tokens) > 1:
                    for token in element.tokens:
                        dfs(token, cols)
                else:
                    cols.append(str(element))
            else:
                if hasattr(element, "tokens"):
                    for token in element.tokens:
                        dfs(token, cols)

        # probs not more than 1 where clause... but just in case
        for where_clause in where_clauses:
            dfs(where_clause, column_names)

        return column_names

    cols = []
    statements = [stmt.strip() for stmt in _leading_comment_remover.sub("", statement).replace("\n", " ").split(";") if stmt.strip()]

    for stmt in statements:
        if op_str := _operation_name(stmt):
            op_type = DatabaseOperation.from_str(op_str)

            match op_type:
                case DatabaseOperation.SELECT | DatabaseOperation.DELETE:
                    cols += parse_where(stmt)
                case DatabaseOperation.UPDATE:
                    # extract list of cols being updated
                    # (where clause not strictly required by sql, but should basically always be present)
                    match = re.search(r"SET +(.*) +WHERE", stmt, re.IGNORECASE)
                    if match:
                        cols += [col_assignment.split("=")[0].strip() for col_assignment in match.group(1).split(",")]
                    cols += parse_where(stmt)
                case DatabaseOperation.INSERT:
                    # extract list of col names before values, if provided
                    match = re.search(r"\((.*)\) +VALUES", stmt, re.IGNORECASE)
                    print(match)
                    if match:
                        cols += [name.strip() for name in match.group(1).split(",")]

    return cols
