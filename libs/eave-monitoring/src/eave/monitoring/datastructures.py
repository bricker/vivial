from dataclasses import dataclass
import dataclasses
from datetime import datetime
from enum import StrEnum
from functools import cache, cached_property
import json
from typing import Any, Optional, Self
from uuid import UUID


type RawEvent = dict[str, Any]

class DatabaseChangeOperation(StrEnum):
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"

    @property
    def hr_past_tense(self) -> str:
        match self:
            case DatabaseChangeOperation.INSERT:
                return "Created"
            case DatabaseChangeOperation.UPDATE:
                return "Updated"
            case DatabaseChangeOperation.DELETE:
                return "Deleted"

@dataclass
class EventPayload:
    def to_dict(self) -> RawEvent:
        return dataclasses.asdict(self)

    def to_json(self) -> str:
        return _compact_json(self.to_dict())

@dataclass
class DatabaseChangeEventPayload(EventPayload):
    table_name: str
    operation: DatabaseChangeOperation
    timestamp: float

    new_data: dict[str, Any] | None
    """JSON string mapping from column names to values"""

    old_data: dict[str, Any] | None
    """JSON string mapping from column names to values"""


@dataclass
class FunctionCallEventPayload(EventPayload):
    function_module: str | None
    function_class: str | None
    function_name: str | None
    function_args: dict[str, Any] | None


@dataclass
class FunctionReturnEventPayload(EventPayload):
    function_module: str
    function_class: str
    function_name: str
    function_args: dict[str, str]
    function_return_value: str


@dataclass
class NetworkInEventPayload(EventPayload):
    request_method: str
    request_path: str
    request_headers: dict[str, str]
    request_payload: str


@dataclass
class NetworkOutEventPayload(EventPayload):
    request_method: str
    request_url: str
    request_headers: dict[str, str]
    request_payload: str

class EventType(StrEnum):
    dbchange = "dbchange"

    @property
    def payload_class(self) -> type[EventPayload]:
        match self:
            case EventType.dbchange:
                return DatabaseChangeEventPayload

@dataclass
class DataIngestRequestBody:
    event_type: EventType
    events: list[str]

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> Self:
        return cls(
            event_type=EventType(value=data["event_type"]),
            events=data["events"],
        )

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)

    def to_json(self) -> str:
        return _compact_json(self.to_dict())


def _compact_json(data: dict[str, Any]) -> str:
    return json.dumps(data, indent=None, separators=(",", ":"))