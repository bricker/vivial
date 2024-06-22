import dataclasses
from typing import Any, cast

from eave.collectors.core.datastructures import DatabaseOperation
from eave.core.internal import database
from eave.core.internal.atoms.api_types import (
    DatabaseEventPayload,
)
from eave.core.internal.atoms.db_record_fields import (
    MultiScalarTypeKeyValueRecordField,
    SessionRecordField,
    TrafficSourceRecordField,
    AccountRecordField,
)
from eave.core.internal.atoms.db_tables import DatabaseEventAtom
from eave.core.internal.atoms.db_views import DatabaseEventView
from eave.core.internal.lib.bq_client import EAVE_INTERNAL_BIGQUERY_CLIENT
from eave.core.internal.orm.virtual_event import VirtualEventOrm
from eave.stdlib.logging import LOGGER, LogContext

from ..table_handle import BigQueryTableHandle


class DatabaseEventsTableHandle(BigQueryTableHandle):
    table_def = DatabaseEventAtom.TABLE_DEF

    async def insert(self, events: list[dict[str, Any]], ctx: LogContext) -> None:
        table = self.get_or_create_table(ctx=ctx)

        unique_operations: set[tuple[DatabaseOperation, str]] = set()
        atoms: list[DatabaseEventAtom] = []

        for payload in events:
            e = DatabaseEventPayload(payload)

            if not e.operation or not e.table_name:
                LOGGER.warning("Missing parameters e.operation and/or e.table_name", ctx)
                continue

            statement_values = (
                MultiScalarTypeKeyValueRecordField.list_from_scalar_dict(e.statement_values)
                if e.statement_values
                else None
            )

            session = None
            traffic_source = None
            user = None

            if e.corr_ctx:
                if e.corr_ctx.session:
                    session = SessionRecordField(resource=e.corr_ctx.session, event_timestamp=e.timestamp)

                if e.corr_ctx.traffic_source:
                    traffic_source = TrafficSourceRecordField(e.corr_ctx.traffic_source)

                if e.corr_ctx.account_id or e.corr_ctx.visitor_id:
                    user = AccountRecordField(account_id=e.corr_ctx.account_id, visitor_id=e.corr_ctx.visitor_id)

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
            unique_operations.add((e.operation, e.table_name))

        errors = EAVE_INTERNAL_BIGQUERY_CLIENT.append_rows(
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
                    team_id=self._team.id,
                ),
            )

            # FIXME: This is a bandaid
            if num_vevents > 1000:
                LOGGER.warning("Max virtual events reached! For safety, no more will be auto-created.", ctx)
                return

        for operation, table_name in unique_operations:
            handle = DatabaseEventView(
                dataset_id=self._dataset_id, event_table_name=table_name, event_operation=operation
            )
            await self.create_bq_view(handle=handle, ctx=ctx)
