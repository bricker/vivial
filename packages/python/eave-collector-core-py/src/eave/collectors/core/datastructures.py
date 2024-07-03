import dataclasses
from abc import ABC
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, ClassVar, Self

from eave.collectors.core.logging import EAVE_LOGGER

from .json import JsonObject, JsonScalar, compact_json

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
            EAVE_LOGGER.warning(e)
            return None

class EventType(StrEnum):
    db_event = "db_event"
    http_server_event = "http_server_event"
    http_client_event = "http_client_event"
    browser_event = "browser_event"
    openai_chat_completion = "openai_chat_completion"


@dataclass(kw_only=True)
class EventPayload(ABC):
    event_type: ClassVar[EventType]
    event_id: str | None
    timestamp: float | None
    corr_ctx: dict[str, JsonScalar] | None

    def to_dict(self) -> JsonObject:
        return dataclasses.asdict(self)

    def to_json(self) -> str:
        return compact_json(self.to_dict())


@dataclass(kw_only=True)
class DatabaseEventPayload(EventPayload):
    event_type: ClassVar[EventType] = EventType.db_event

    operation: str | None = None
    db_name: str | None = None
    table_name: str | None = None
    statement: str | None = None
    statement_values: dict[str, Any] | None = None

@dataclass(kw_only=True)
class HttpServerEventPayload(EventPayload):
    """Data about a request being handled by server application code"""

    event_type: ClassVar[EventType] = EventType.http_server_event

    request_method: str | None = None
    request_url: str | None = None
    request_headers: dict[str, str] | None = None
    request_payload: str | None = None


@dataclass
class HttpClientEventPayload(EventPayload):
    """Data about requests made by application code"""

    event_type: ClassVar[EventType] = EventType.http_client_event

    request_method: str | None = None
    request_url: str | None = None
    request_headers: dict[str, str] | None = None
    request_payload: str | None = None


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
