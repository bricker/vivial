import dataclasses
from dataclasses import dataclass
from textwrap import dedent
from typing import Any, cast
import inflect

from google.cloud.bigquery import SchemaField, SqlTypeNames, StandardSqlTypeNames

from eave.collectors.core.datastructures import DatabaseEventPayload, DatabaseOperation
from eave.core.internal import database
from eave.core.internal.atoms.api_types import (
    CorrelationContext,
)
from eave.core.internal.atoms.record_fields import (
    MultiScalarTypeKeyValueRecordField,
    SessionRecordField,
    TrafficSourceRecordField,
    UserRecordField,
)
from eave.core.internal.atoms.shared import common_bq_insert_timestamp_field, common_event_timestamp_field
from eave.core.internal.orm.virtual_event import VirtualEventOrm
from eave.stdlib.logging import LOGGER, LogContext
from eave.stdlib.util import sql_sanitized_identifier, sql_sanitized_literal, tableize, titleize

from .table_handle import BigQueryFieldMode, BigQueryTableDefinition, BigQueryTableHandle


@dataclass(kw_only=True)
class DatabaseEventAtom:
    @staticmethod
    def schema() -> tuple[SchemaField, ...]:
        return (
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
            common_event_timestamp_field(),
            SchemaField(
                name="statement",
                description="The full database statement.",
                field_type=StandardSqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            MultiScalarTypeKeyValueRecordField.schema(
                name="statement_values",
                description="The SQL parameter values passed into the statement.",
            ),
            SessionRecordField.schema(),
            UserRecordField.schema(),
            TrafficSourceRecordField.schema(),
            common_bq_insert_timestamp_field(),
        )

    operation: str | None
    db_name: str | None
    table_name: str | None
    timestamp: float | None
    statement: str | None
    statement_values: list[MultiScalarTypeKeyValueRecordField] | None
    session: SessionRecordField | None
    user: UserRecordField | None
    traffic_source: TrafficSourceRecordField | None


class DatabaseEventsTableHandle(BigQueryTableHandle):
    table_def = BigQueryTableDefinition(
        table_id="atoms_db_events",
        friendly_name="Database atoms",
        description="Database atoms",
        schema=DatabaseEventAtom.schema(),
    )

    async def insert(self, events: list[dict[str, Any]], ctx: LogContext) -> None:
        if len(events) == 0:
            return

        self._bq_client.get_or_create_dataset(dataset_id=self.dataset_id)

        table = self._bq_client.get_or_create_table(
            table=self.construct_bq_table(),
            ctx=ctx,
        )

        unique_operations: set[tuple[str, str]] = set()
        atoms: list[DatabaseEventAtom] = []

        for payload in events:
            e: DatabaseEventPayload | None = None

            try:
                e = DatabaseEventPayload(**payload)
            except Exception as err:
                LOGGER.exception(err, ctx)
                continue

            if not e.operation or not e.table_name:
                LOGGER.warning("Missing parameters e.operation and/or e.table_name", ctx)
                continue

            db_operation = DatabaseOperation.from_str(e.operation)
            if not db_operation:
                LOGGER.warning("Unknown database operation", {"operation": e.operation}, ctx)
                continue

            unique_operations.add((e.operation, e.table_name))

            statement_values = (
                MultiScalarTypeKeyValueRecordField.list_from_scalar_dict(e.statement_values) if e.statement_values else None
            )

            corr_ctx = CorrelationContext.from_api_payload(e.corr_ctx) if e.corr_ctx else None
            session = (
                SessionRecordField.from_api_resource(resource=corr_ctx.session, event_timestamp=e.timestamp)
                if corr_ctx
                else None
            )
            traffic_source = TrafficSourceRecordField.from_api_resource(corr_ctx.traffic_source) if corr_ctx else None
            user = UserRecordField(account_id=corr_ctx.account_id, visitor_id=corr_ctx.visitor_id) if corr_ctx else None

            atom = DatabaseEventAtom(
                operation=e.operation,
                db_name=e.db_name,
                table_name=e.table_name,
                timestamp=e.timestamp,
                statement=e.statement,
                statement_values=statement_values,
                session=session,
                user=user,
                traffic_source=traffic_source,
            )

            atoms.append(atom)

        errors = self._bq_client.append_rows(
            table=table,
            rows=[dataclasses.asdict(atom) for atom in atoms],
        )

        if len(errors) > 0:
            LOGGER.warning("BigQuery insert errors", {"errors": cast(list, errors)}, ctx)

        # FIXME: The following band-aid checks are a safety measure against unexpectedly creating an excessive number of virtual events.
        # This could happen due to a programming error, or due to a malicious payload.
        # BigQuery allows effectively unlimited tables per dataset, and there is effectively no limit on Virtual Event rows in our Postgres database.
        # However, it'd be trivial to insert database atoms with a randomly-generated table name, and cause views to be created for each one.
        # If that happened, it's either unintentional or malicious; either way we should prevent it from happening.
        if len(unique_operations) > 50:
            LOGGER.warning("Too many unique operations. For safety, views will not be auto-created.", ctx)
            return

        async with database.async_session.begin() as db_session:
            num_vevents = await VirtualEventOrm.count(
                session=db_session,
                params=VirtualEventOrm.QueryParams(
                    team_id=self.team.id,
                ),
            )

            # FIXME: This is a bandaid
            if num_vevents > 1000:
                LOGGER.warning("Max virtual events reached! For safety, no more will be auto-created.", ctx)
                return

        for operation, table_name in unique_operations:
            await self._create_vevent_view(operation=operation, source_table=table_name, ctx=ctx)

    async def _create_vevent_view(self, *, operation: str, source_table: str, ctx: LogContext) -> None:
        table_resource = titleize(source_table)
        operation_verb = _operation_readable_verb_past_tense(operation)
        vevent_readable_name = f"{operation_verb} {table_resource}"
        vevent_description = _make_vevent_description(operation=operation, source_table=source_table)
        vevent_view_id = tableize(vevent_readable_name)

        async with database.async_session.begin() as db_session:
            existing_vevent = (
                await VirtualEventOrm.query(
                    session=db_session,
                    params=VirtualEventOrm.QueryParams(
                        team_id=self.team.id,
                        view_id=vevent_view_id,
                    ),
                )
            ).one_or_none()

            if existing_vevent:
                return

            sanitized_dataset_id = sql_sanitized_identifier(self.dataset_id)
            sanitized_atom_table_id = sql_sanitized_identifier(self.table_def.table_id)
            sanitized_source_table = sql_sanitized_literal(source_table)
            sanitized_operation = sql_sanitized_literal(operation)
            sanitized_readable_name = sql_sanitized_literal(vevent_readable_name)

            view = self._bq_client.construct_table(dataset_id=self.dataset_id, table_id=vevent_view_id)
            view.friendly_name = vevent_readable_name
            view.description = vevent_description

            view.view_query = dedent(
                f"""
                SELECT
                    {sanitized_readable_name} as `event_name`,
                    `timestamp`,
                    `user`,
                    `session`,
                    `traffic_source`,
                FROM
                    {sanitized_dataset_id}.{sanitized_atom_table_id}
                WHERE
                    `table_name` = {sanitized_source_table}
                    AND `operation` = {sanitized_operation}
                ORDER BY
                    `timestamp` ASC
                """
            ).strip()

            view = self._bq_client.get_or_create_table(
                table=view,
                ctx=ctx,
            )

            view.schema = (
                SchemaField(
                    name="event_name",
                    description=f"A readable name for this event. Always '{vevent_readable_name}'.",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                common_event_timestamp_field(),
                UserRecordField.schema(),
                SessionRecordField.schema(),
                TrafficSourceRecordField.schema(),
            )

            view = self._bq_client.update_table(table=view, ctx=ctx)

            try:
                await VirtualEventOrm.create(
                    session=db_session,
                    team_id=self.team.id,
                    view_id=view.table_id,
                    readable_name=vevent_readable_name,
                    description=vevent_description,
                )
            except Exception as e:
                # Likely a race condition: Two events came in separate requests that tried to create the same virtual event.
                LOGGER.exception(e)


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


def _make_vevent_description(operation: str, source_table: str) -> str:
    e = inflect.engine()

    db_operation = DatabaseOperation.from_str(operation)
    resource = titleize(source_table)
    if not isinstance(resource, inflect.Word):
        aresource = resource
    else:
        aresource = e.a(resource)

    match db_operation:
        case DatabaseOperation.INSERT:
            description = f"{aresource} was created."
        case DatabaseOperation.UPDATE:
            description = f"{aresource} as updated."
        case DatabaseOperation.DELETE:
            description = f"{aresource} was deleted."
        case DatabaseOperation.SELECT:
            description = f"{aresource} was fetched."
        case _:
            # TODO: What verb to use for an invalid DatabaseOperation value?
            description = f"{aresource} was inspected."

    return description.title()
