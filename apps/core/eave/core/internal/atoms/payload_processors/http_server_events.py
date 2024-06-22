import dataclasses
from typing import Any, cast

from eave.collectors.core.datastructures import HttpRequestMethod
from eave.core.internal.atoms.api_types import HttpServerEventPayload
from eave.core.internal.atoms.db_record_fields import (
    SessionRecordField,
    SingleScalarTypeKeyValueRecordField,
    TrafficSourceRecordField,
    AccountRecordField,
)
from eave.core.internal.atoms.db_tables import HttpServerEventAtom
from eave.core.internal.atoms.db_views import HttpServerEventView
from eave.core.internal.lib.bq_client import EAVE_INTERNAL_BIGQUERY_CLIENT
from eave.stdlib.logging import LOGGER, LogContext

from ..table_handle import BigQueryTableHandle


class HttpServerEventsTableHandle(BigQueryTableHandle):
    table_def = HttpServerEventAtom.TABLE_DEF

    async def insert(self, events: list[dict[str, Any]], ctx: LogContext) -> None:
        table = self.get_or_create_table(ctx=ctx)

        unique_operations: set[HttpRequestMethod] = set()
        atoms: list[HttpServerEventAtom] = []

        for payload in events:
            e = HttpServerEventPayload(payload)

            if not e.request_method or not e.request_url:
                LOGGER.warning("Invalid server event payload", ctx)
                continue

            request_headers = (
                SingleScalarTypeKeyValueRecordField[str].list_from_scalar_dict(e.request_headers)
                if e.request_headers
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

            atom = HttpServerEventAtom(
                request_method=e.request_method,
                request_headers=request_headers,
                request_url=e.request_url,
                request_payload=e.request_payload,
                timestamp=e.timestamp,
                session=session,
                user=user,
                traffic_source=traffic_source,
            )

            atoms.append(atom)
            unique_operations.add(e.request_method)

        errors = EAVE_INTERNAL_BIGQUERY_CLIENT.append_rows(
            table=table,
            rows=[dataclasses.asdict(atom) for atom in atoms],
        )

        if len(errors) > 0:
            LOGGER.warning("BigQuery insert errors", {"errors": cast(list, errors)}, ctx)

        for request_method in unique_operations:
            handle = HttpServerEventView(dataset_id=self._dataset_id, request_method=request_method)
            await self.create_bq_view(handle=handle, ctx=ctx)
