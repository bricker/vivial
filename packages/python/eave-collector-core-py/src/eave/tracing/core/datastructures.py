from dataclasses import dataclass
import dataclasses
from enum import StrEnum
import json
from typing import Any, Self
import pydantic

type RawEvent = dict[str, Any]

class DatabaseStructure(StrEnum):
    UNKNOWN = "unknown"
    SQL = "SQL"
    NO_SQL = "noSQL"

    @classmethod
    def from_str(cls, s: str) -> Self | None:
        try:
            return cls.__call__(value=s.upper())
        except:
            return None

class DatabaseOperation(StrEnum):
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    SELECT = "SELECT"

    @classmethod
    def from_str(cls, s: str) -> Self | None:
        try:
            return cls.__call__(value=s.upper())
        except:
            return None

    @property
    def hr_past_tense(self) -> str:
        match self:
            case DatabaseOperation.INSERT:
                return "Created"
            case DatabaseOperation.UPDATE:
                return "Updated"
            case DatabaseOperation.DELETE:
                return "Deleted"
            case DatabaseOperation.SELECT:
                return "Queried"


@dataclass
class EventPayload:
    def to_dict(self) -> RawEvent:
        return dataclasses.asdict(self)

    def to_json(self) -> str:
        return _compact_json(self.to_dict())


@dataclass
class DatabaseEventPayload(EventPayload):
    statement: str
    parameters: list[str] | None
    timestamp: float
    db_structure: DatabaseStructure


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
    dbevent = "dbevent"

    @property
    def payload_class(self) -> type[EventPayload]:
        match self:
            case EventType.dbevent:
                return DatabaseEventPayload


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
