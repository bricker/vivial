from dataclasses import dataclass
from typing import Any, Self


@dataclass(kw_only=True)
class AtomCollectorLogRecord:
    name: str | None
    """Name of the collector from which the log originated"""
    level: str | None
    pathname: str | None
    line_number: int | None
    msg: str | None

    @classmethod
    def from_api_payload(cls, data: dict[str, Any]) -> Self:
        return cls(
            name=data.get("name"),
            level=data.get("level"),
            pathname=data.get("pathname"),
            line_number=data.get("line_number"),
            msg=data.get("msg"),
        )
