import dataclasses
from typing import Any

from google.cloud.logging import Client as CloudLogClient

from eave.core.internal.atoms.models.collector_logs import AtomCollectorLogRecord
from eave.stdlib.logging import LogContext

from .base_atom_controller import BaseAtomController


class AtomCollectorLogsController(BaseAtomController):
    async def insert(self, raw_logs: list[dict[str, Any]], ctx: LogContext) -> None:
        cloud_logger = CloudLogClient().logger("collector_log")

        logs = [AtomCollectorLogRecord.from_api_payload(payload) for payload in raw_logs]

        if len(logs) == 0:
            return

        for log in logs:
            cloud_logger.log_text(
                text=log.msg,
                # sev levels: https://cloud.google.com/logging/docs/reference/v2/rest/v2/LogEntry#logseverity
                severity=log.level.upper() if log.level else "DEFAULT",
                # just slap in other fields as labels for now...
                labels={k: str(v) for k, v in dataclasses.asdict(log).items() if v and k not in ("msg", "level")},
            )
