import dataclasses
from typing import Any, cast
from eave.stdlib.logging import LOGGER, LogContext

from eave.core.internal.atoms.models.collector_logs import AtomCollectorLogRecord
from eave.core.internal.lib.bq_client import EAVE_INTERNAL_BIGQUERY_CLIENT
from .base_atom_controller import BaseAtomController


class AtomCollectorLogsController(BaseAtomController):
    async def insert(self, raw_logs: list[dict[str, Any]], ctx: LogContext) -> None:
        # TODO: convert to send data to cloud logging instead of bq
        table = self.get_or_create_bq_table(table_def=AtomCollectorLogRecord.table_def(), ctx=ctx)

        logs = [
            AtomCollectorLogRecord.from_api_payload(payload, decryption_key=self._client.decryption_key)
            for payload in raw_logs
        ]

        if len(logs) == 0:
            return

        errors = EAVE_INTERNAL_BIGQUERY_CLIENT.append_rows(
            table=table,
            rows=[dataclasses.asdict(log) for log in logs],
        )

        if len(errors) > 0:
            LOGGER.warning("BigQuery insert errors", {"errors": cast(list, errors)}, ctx)
