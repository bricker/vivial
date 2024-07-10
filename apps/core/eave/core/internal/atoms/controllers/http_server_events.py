import dataclasses
from typing import Any, cast

from eave.core.internal.atoms.models.api_payload_types import HttpServerEventPayload
from eave.core.internal.atoms.models.atom_types import HttpServerEventAtom
from eave.core.internal.atoms.models.db_record_fields import (
    AccountRecordField,
    MetadataRecordField,
    SessionRecordField,
    SingleScalarTypeKeyValueRecordField,
    TrafficSourceRecordField,
    UrlRecordField,
)
from eave.core.internal.lib.bq_client import EAVE_INTERNAL_BIGQUERY_CLIENT
from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.deidentification import redact_atoms
from eave.stdlib.logging import LOGGER, LogContext

from .base_atom_controller import BaseAtomController


class HttpServerEventsController(BaseAtomController):
    async def insert(self, events: list[dict[str, Any]], ctx: LogContext) -> None:
        table = self.get_or_create_bq_table(table_def=HttpServerEventAtom.table_def(), ctx=ctx)
        atoms: list[HttpServerEventAtom] = []

        for payload in events:
            e = HttpServerEventPayload.from_api_payload(payload, decryption_key=self._client.decryption_key)

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

            atom = HttpServerEventAtom(
                event_id=e.event_id,
                timestamp=e.timestamp,
                request_method=e.request_method,
                request_headers=request_headers,
                request_url=UrlRecordField.from_api_resource(e.request_url),
                request_payload=e.request_payload,
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

        await redact_atoms(atoms)

        errors = EAVE_INTERNAL_BIGQUERY_CLIENT.append_rows(
            table=table,
            rows=[dataclasses.asdict(atom) for atom in atoms],
        )

        if len(errors) > 0:
            LOGGER.warning("BigQuery insert errors", {"errors": cast(list, errors)}, ctx)
