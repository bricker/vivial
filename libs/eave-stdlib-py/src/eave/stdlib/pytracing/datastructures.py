
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

class EventType(StrEnum):
    functioncall = "functioncall"
    functionreturn = "functionreturn"
    networkin = "networkin"
    networkout = "networkout"
    dbchange = "dbchange"


class EventParams:
    pass

@dataclass
class PostgresDatabaseChangeEventParams(EventParams):
    table_name: str
    operation: str
    operated_data: str # JSON string mapping from column names to values

@dataclass
class FunctionCallEventParams(EventParams):
    function_module: str | None
    function_class: str | None
    function_name: str | None
    function_args: dict[str, Any] | None

@dataclass
class FunctionReturnEventParams(EventParams):
    function_module: str
    function_class: str
    function_name: str
    function_args: dict[str, str]
    function_return_value: str

@dataclass
class NetworkInEventParams(EventParams):
    request_method: str
    request_path: str
    request_headers: dict[str, str]
    request_payload: str

@dataclass
class NetworkOutEventParams(EventParams):
    request_method: str
    request_url: str
    request_headers: dict[str,str]
    request_payload: str

@dataclass
class RawEvent:
    team_id: UUID
    corr_id: UUID
    timestamp: datetime
    event_type: EventType
    event_params: EventParams