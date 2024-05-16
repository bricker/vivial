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
    timestamp: float
    parameters: dict[str, Any] | None


@dataclass(kw_only=True, init=False)
class BrowserEventPayload(EventPayload):
    event_type: ClassVar[EventType] = EventType.browser_event

    action_name: str | None
    idsite: str | None
    h: str | None
    m: str | None
    s: str | None
    e_c: str | None
    e_a: str | None
    e_n: str | None
    e_v: str | None
    e_ts: str | None
    url: str | None
    queryParams: str | None  # noqa: N815
    _eave_visitor_id: str | None
    _eave_session_id: str | None
    pv_id: str | None
    pf_net: str | None
    pf_srv: str | None
    pf_tfr: str | None
    pf_dm1: str | None
    eaveClientId: str | None  # noqa: N815
    uadata: str | None
    pdf: str | None
    qt: str | None
    realp: str | None
    wma: str | None
    fla: str | None
    java: str | None
    ag: str | None
    cookie: str | None
    res: str | None

    _extra: dict[str, Any] | None = None

    def __init__(self,
        *,
        context: dict[str, Any] | None = None,
        action_name: str | None = None,
        idsite: str | None = None,
        h: str | None = None,
        m: str | None = None,
        s: str | None = None,
        e_c: str | None = None,
        e_a: str | None = None,
        e_n: str | None = None,
        e_v: str | None = None,
        e_ts: str | None = None,
        url: str | None = None,
        queryParams: str | None   = None,  # noqa: N803
        _eave_visitor_id: str | None = None,
        _eave_session_id: str | None = None,
        pv_id: str | None = None,
        pf_net: str | None = None,
        pf_srv: str | None = None,
        pf_tfr: str | None = None,
        pf_dm1: str | None = None,
        eaveClientId: str | None  = None,  # noqa: N803
        uadata: str | None = None,
        pdf: str | None = None,
        qt: str | None = None,
        realp: str | None = None,
        wma: str | None = None,
        fla: str | None = None,
        java: str | None = None,
        ag: str | None = None,
        cookie: str | None = None,
        res: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(context=context)

        self.action_name = action_name
        self.idsite = idsite
        self.h = h
        self.m = m
        self.s = s
        self.e_c = e_c
        self.e_a = e_a
        self.e_n = e_n
        self.e_v = e_v
        self.e_ts = e_ts
        self.url = url
        self.queryParams = queryParams
        self._eave_visitor_id = _eave_visitor_id
        self._eave_session_id = _eave_session_id
        self.pv_id = pv_id
        self.pf_net = pf_net
        self.pf_srv = pf_srv
        self.pf_tfr = pf_tfr
        self.pf_dm1 = pf_dm1
        self.eaveClientId = eaveClientId
        self.uadata = uadata
        self.pdf = pdf
        self.qt = qt
        self.realp = realp
        self.wma = wma
        self.fla = fla
        self.java = java
        self.ag = ag
        self.cookie = cookie
        self.res = res

        self._extra = kwargs

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
