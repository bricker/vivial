import dataclasses
import logging
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, ClassVar, Self

from .json import JsonObject, compact_json


class DatabaseStructure(StrEnum):
    UNKNOWN = "unknown"
    SQL = "SQL"
    NO_SQL = "noSQL"

    @classmethod
    def from_str(cls, s: str) -> Self | None:
        try:
            return cls.__call__(value=s.upper())
        except ValueError as e:
            logging.getLogger().warning(e)
            return None


class DatabaseOperation(StrEnum):
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    SELECT = "SELECT"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def from_str(cls, s: str) -> Self | None:
        try:
            return cls.__call__(value=s.upper())
        except ValueError as e:
            logging.getLogger().warning(e)
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
            case _:
                return "Inspected"  # idk


class EventType(StrEnum):
    db_event = "db_event"
    http_server_event = "http_server_event"
    http_client_event = "http_client_event"
    function_call = "function_call"
    function_return = "function_return"
    browser_event = "browser_event"


@dataclass(kw_only=True)
class EventPayload:
    event_type: ClassVar[EventType]

    timestamp: float | None
    context: dict[str, Any] | None

    def to_dict(self) -> JsonObject:
        return dataclasses.asdict(self)

    def to_json(self) -> str:
        return compact_json(self.to_dict())


@dataclass(kw_only=True)
class DatabaseEventPayload(EventPayload):
    event_type: ClassVar[EventType] = EventType.db_event

    statement: str | None
    db_structure: DatabaseStructure
    db_name: str | None
    table_name: str | None
    operation: str | None
    parameters: dict[str, Any] | None

@dataclass(kw_only=True)
class FunctionCallEventPayload(EventPayload):
    event_type: ClassVar[EventType] = EventType.function_call

    function_module: str | None
    function_class: str | None
    function_name: str | None
    function_args: dict[str, Any] | None


@dataclass(kw_only=True)
class FunctionReturnEventPayload(EventPayload):
    event_type: ClassVar[EventType] = EventType.function_return

    function_module: str
    function_class: str
    function_name: str
    function_args: dict[str, str]
    function_return_value: str


@dataclass(kw_only=True)
class HttpServerEventPayload(EventPayload):
    """Data about a request being handled by server application code"""

    event_type: ClassVar[EventType] = EventType.http_server_event

    request_method: str
    request_url: str
    request_headers: dict[str, str]
    request_payload: str


@dataclass
class HttpClientEventPayload(EventPayload):
    """Data about requests made by application code"""

    event_type: ClassVar[EventType] = EventType.http_client_event

    request_method: str
    request_url: str
    request_headers: dict[str, str]
    request_payload: str


@dataclass
class DataIngestRequestBody:
    events: dict[str, list[JsonObject]]
    """map from event_type name to list of events of that type"""

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> Self:
        return cls(
            events=data["events"],
        )

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)

    def to_json(self) -> str:
        return compact_json(self.to_dict())
