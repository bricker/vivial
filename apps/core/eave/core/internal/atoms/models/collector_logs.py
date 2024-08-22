from dataclasses import dataclass
from typing import Any, Self
from eave.stdlib.core_api.models.virtual_event import BigQueryFieldMode
from google.cloud.bigquery import SchemaField, SqlTypeNames

from eave.core.internal.atoms.models.atom_types import BigQueryTableDefinition


@dataclass(kw_only=True)
class AtomCollectorLogRecord:
    @staticmethod
    def table_def() -> BigQueryTableDefinition:
        return BigQueryTableDefinition(
            table_id="atom_collector_logs",
            friendly_name="Atom Collector Logs",
            description="Event logs from Eave's atom collectors in the wild.",
            schema=(
                SchemaField(
                    name="name",
                    description="The logger's name.",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                SchemaField(
                    name="level",
                    description="Log level (e.g. ERROR, WARNING, INFO)",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                SchemaField(
                    name="pathname",
                    description="File path at which the log was written.",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                SchemaField(
                    name="line_number",
                    description="File line number of the file at `pathname` at which the log was written.",
                    field_type=SqlTypeNames.INTEGER,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                SchemaField(
                    name="message",
                    description="The log message content.",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
            ),
        )

    name: str | None
    level: str | None
    pathname: str | None
    line_number: int | None
    msg: str | None
    # TODO: add a timestamp??

    @classmethod
    def from_api_payload(cls, data: dict[str, Any], *, decryption_key: bytes) -> Self:
        return cls(
            name=data.get("name"),
            level=data.get("level"),
            pathname=data.get("pathname"),
            line_number=data.get("line_number"),
            msg=data.get("msg"),
        )
