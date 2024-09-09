import dataclasses
import logging
from abc import ABC
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, ClassVar, Self

from .json import JsonObject, JsonScalar, JsonValue, compact_json


class DatabaseOperation(StrEnum):
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    SELECT = "SELECT"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def from_str(cls, s: str) -> Self:
        try:
            return cls.__call__(value=s.upper())
        except ValueError:
            return cls(value=cls.UNKNOWN)


class EventType(StrEnum):
    db_event = "db_event"
    http_server_event = "http_server_event"
    http_client_event = "http_client_event"
    browser_event = "browser_event"
    openai_chat_completion = "openai_chat_completion"


@dataclass(kw_only=True)
class StackFrame:
    filename: str | None
    function: str | None


@dataclass
class Batchable(ABC):
    def to_dict(self) -> JsonObject:
        return dataclasses.asdict(self)

    def to_json(self) -> str:
        return compact_json(self.to_dict())


@dataclass(kw_only=True)
class LogPayload(Batchable):
    name: str
    """Name of the collector that created the log"""
    level: str
    pathname: str
    line_number: int
    msg: str

    @classmethod
    def from_record(cls, log: logging.LogRecord) -> Self:
        return cls(
            # rely on eave logger builder to have added the package name to the logger name.
            # split the eave base logger name off the front, assuming package name is the rest
            name=".".join(log.name.split(".")[1:]),
            level=log.levelname,
            pathname=log.pathname,
            line_number=log.lineno,
            msg=log.getMessage(),
        )


@dataclass(kw_only=True)
class EventPayload(Batchable, ABC):
    event_type: ClassVar[EventType]
    event_id: str | None
    timestamp: float | None
    corr_ctx: dict[str, JsonScalar] | None


@dataclass(kw_only=True)
class DatabaseEventPayload(EventPayload):
    event_type: ClassVar[EventType] = EventType.db_event

    operation: DatabaseOperation | None = None
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


@dataclass(kw_only=True)
class HttpClientEventPayload(EventPayload):
    """Data about requests made by application code"""

    event_type: ClassVar[EventType] = EventType.http_client_event

    request_method: str | None = None
    request_url: str | None = None
    request_headers: dict[str, str] | None = None
    request_payload: str | None = None


@dataclass(kw_only=True)
class OpenAIRequestProperties:
    request_params: dict[str, JsonValue] | None
    start_timestamp: float | None
    end_timestamp: float | None


@dataclass(kw_only=True)
class OpenAIChatCompletionEventPayload(EventPayload):
    event_type: ClassVar[EventType] = EventType.openai_chat_completion

    completion_id: str | None
    completion_system_fingerprint: str | None
    completion_created_timestamp: float | None
    completion_user_id: str | None
    service_tier: str | None
    model: str | None
    prompt_tokens: int | None
    completion_tokens: int | None
    total_tokens: int | None
    stack_frames: list[StackFrame] | None
    openai_request: OpenAIRequestProperties | None


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


@dataclass
class LogIngestRequestBody:
    logs: list[JsonObject]

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> Self:
        return cls(
            logs=data["logs"],
        )

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)

    def to_json(self) -> str:
        return compact_json(self.to_dict())
