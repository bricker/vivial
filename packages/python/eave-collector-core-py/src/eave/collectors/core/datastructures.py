import dataclasses
import json
import logging
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Mapping, Self, Sequence

from eave.collectors.core.json import compact_json
from eave.stdlib.typing import JsonObject

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
                return "Inspected" # idk

@dataclass
class EventPayload:
    def to_dict(self) -> JsonObject:
        return dataclasses.asdict(self)

    def to_json(self) -> str:
        return compact_json(self.to_dict())

@dataclass
class DatabaseEventPayload(EventPayload):
    statement: str | None
    db_name: str | None
    table_name: str | None
    operation: str | None
    timestamp: float
    db_structure: DatabaseStructure
    parameters: Any | None
    records: list[dict[str, Any]] | None

# @dataclass
# class DatabaseInsertEventPayload(DatabaseEventPayload):
#     inserted_records: list[dict[str, Any]]

# @dataclass
# class DatabaseUpdateEventPayload(EventPayload):
#     updated_records: list[dict[str, Any]]

# @dataclass
# class DatabaseDeleteEventPayload(EventPayload):
#     deleted_records: list[dict[str, Any]]

# @dataclass
# class DatabaseSelectEventPayload(EventPayload):
#     selected_records: list[dict[str, Any]]


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
        return compact_json(self.to_dict())
