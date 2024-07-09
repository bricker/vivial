import dataclasses
from typing import Any, cast

from eave.collectors.core.datastructures import DatabaseOperation
from eave.stdlib.config import SHARED_CONFIG
from eave.core.internal import database
from eave.core.internal.atoms.models.api_payload_types import (
    DatabaseEventPayload,
)
from eave.core.internal.atoms.models.atom_types import DatabaseEventAtom
from eave.core.internal.atoms.models.db_record_fields import (
    AccountRecordField,
    MetadataRecordField,
    MultiScalarTypeKeyValueRecordField,
    SessionRecordField,
    TrafficSourceRecordField,
)
from eave.core.internal.atoms.models.db_views import DatabaseEventView
from eave.core.internal.lib.bq_client import EAVE_INTERNAL_BIGQUERY_CLIENT
from eave.core.internal.orm.virtual_event import VirtualEventOrm
from eave.stdlib.deidentification import redact_atoms
from eave.stdlib.logging import LOGGER, LogContext

from .base_atom_controller import BaseAtomController


class DatabaseEventsController(BaseAtomController):
    async def insert(self, events: list[dict[str, Any]], ctx: LogContext) -> None:
        table = self.get_or_create_bq_table(table_def=DatabaseEventAtom.table_def(), ctx=ctx)

        unique_operations: set[tuple[DatabaseOperation, str]] = set()
        atoms: list[DatabaseEventAtom] = []

        for payload in events:
            e = DatabaseEventPayload.from_api_payload(payload, decryption_key=self._client.decryption_key)

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
            account = None
            visitor_id = None

            if e.corr_ctx:
                visitor_id = e.corr_ctx.visitor_id

                if e.corr_ctx.session:
                    session = SessionRecordField.from_api_resource(
                        resource=e.corr_ctx.session, event_timestamp=e.timestamp
                    )

                if e.corr_ctx.traffic_source:
                    traffic_source = TrafficSourceRecordField.from_api_resource(e.corr_ctx.traffic_source)

                if e.corr_ctx.account:
                    account = AccountRecordField.from_api_resource(e.corr_ctx.account)

            atom = DatabaseEventAtom(
                event_id=e.event_id,
                timestamp=e.timestamp,
                operation=e.operation,
                db_name=e.db_name,
                table_name=e.table_name,
                statement=e.statement,
                statement_values=statement_values,
                session=session,
                account=account,
                traffic_source=traffic_source,
                visitor_id=visitor_id,
                metadata=MetadataRecordField(
                    source_app_name=SHARED_CONFIG.app_service,
                    source_app_version=SHARED_CONFIG.app_version,
                    source_app_release_timestamp=SHARED_CONFIG.release_timestamp,
                ),
            )

            atoms.append(atom)
            unique_operations.add((e.operation, e.table_name))

        await redact_atoms(atoms)

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
                    team_id=self._client.team_id,
                ),
            )

            # FIXME: This is a bandaid
            if num_vevents > 1000:
                LOGGER.warning("Max virtual events reached! For safety, no more will be auto-created.", ctx)
                return

        for operation, table_name in unique_operations:
            view_def = DatabaseEventView(event_table_name=table_name, event_operation=operation)
            await self.sync_bq_view(view_def=view_def, ctx=ctx)
