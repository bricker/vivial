import dataclasses
from typing import Any, cast

from eave.core.internal.atoms.api_types import BrowserAction, BrowserEventPayload
from eave.core.internal.atoms.atom_types import BrowserEventAtom
from eave.core.internal.atoms.db_record_fields import (
    AccountRecordField,
    CurrentPageRecordField,
    DeviceRecordField,
    GeoRecordField,
    MultiScalarTypeKeyValueRecordField,
    SessionRecordField,
    TargetRecordField,
    TrafficSourceRecordField,
)
from eave.core.internal.atoms.db_views import ClickView, FormSubmissionView, PageViewView
from eave.core.internal.atoms.table_handle import BigQueryTableHandle
from eave.core.internal.lib.bq_client import EAVE_INTERNAL_BIGQUERY_CLIENT
from eave.stdlib.logging import LOGGER, LogContext


class BrowserEventsTableHandle(BigQueryTableHandle):
    table_def = BrowserEventAtom.TABLE_DEF

    async def insert_with_geolocation(
        self, events: list[dict[str, Any]], geolocation: GeoRecordField | None, client_ip: str | None, ctx: LogContext
    ) -> None:
        table = self.get_or_create_table(ctx=ctx)

        unique_operations: set[BrowserAction] = set()
        atoms: list[BrowserEventAtom] = []

        for payload in events:
            e = BrowserEventPayload.from_api_payload(payload, decryption_key=self._client.decryption_key)
            if not e.action:
                LOGGER.warning("Unexpected event action", {"event": payload}, ctx)
                continue

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

            atom = BrowserEventAtom(
                action=e.action,
                timestamp=e.timestamp,
                session=session,
                account=account,
                traffic_source=traffic_source,
                target=TargetRecordField.from_api_resource(e.target) if e.target else None,
                current_page=CurrentPageRecordField.from_api_resource(e.current_page) if e.current_page else None,
                device=DeviceRecordField.from_api_resource(e.device) if e.device else None,
                geo=geolocation,
                extra=MultiScalarTypeKeyValueRecordField.list_from_scalar_dict(e.extra) if e.extra else None,
                client_ip=client_ip,
                visitor_id=visitor_id,
            )

            atoms.append(atom)
            unique_operations.add(e.action)

        formatted_rows = [dataclasses.asdict(atom) for atom in atoms]
        errors = EAVE_INTERNAL_BIGQUERY_CLIENT.append_rows(
            table=table,
            rows=formatted_rows,
        )

        if len(errors) > 0:
            LOGGER.warning("BigQuery insert errors", {"errors": cast(list, errors)}, ctx)

        for action in unique_operations:
            match action:
                case BrowserAction.CLICK:
                    handle = ClickView(dataset_id=self._dataset_id)
                case BrowserAction.FORM_SUBMISSION:
                    handle = FormSubmissionView(dataset_id=self._dataset_id)
                case BrowserAction.PAGE_VIEW:
                    handle = PageViewView(dataset_id=self._dataset_id)
                case _:
                    LOGGER.warning(f"Unsupported action: {action}", ctx)
                    return

            await self.create_bq_view(handle=handle, ctx=ctx)
