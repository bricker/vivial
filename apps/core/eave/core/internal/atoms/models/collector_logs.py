from dataclasses import dataclass
from typing import Any, Self
from eave.stdlib.core_api.models.virtual_event import BigQueryFieldMode
from google.cloud.bigquery import SchemaField, SqlTypeNames

from eave.core.internal.atoms.models.atom_types import BigQueryTableDefinition


@dataclass(kw_only=True)
class AtomCollectorLogRecord:
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
