from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class EaveEvent(_message.Message):
    __slots__ = ["eave_account_id", "eave_env", "eave_team_id", "eave_visitor_id", "event_description", "event_name", "event_source", "event_ts", "opaque_params"]
    EAVE_ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    EAVE_ENV_FIELD_NUMBER: _ClassVar[int]
    EAVE_TEAM_ID_FIELD_NUMBER: _ClassVar[int]
    EAVE_VISITOR_ID_FIELD_NUMBER: _ClassVar[int]
    EVENT_DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    EVENT_NAME_FIELD_NUMBER: _ClassVar[int]
    EVENT_SOURCE_FIELD_NUMBER: _ClassVar[int]
    EVENT_TS_FIELD_NUMBER: _ClassVar[int]
    OPAQUE_PARAMS_FIELD_NUMBER: _ClassVar[int]
    eave_account_id: str
    eave_env: str
    eave_team_id: str
    eave_visitor_id: str
    event_description: str
    event_name: str
    event_source: str
    event_ts: float
    opaque_params: str
    def __init__(self, event_name: _Optional[str] = ..., event_description: _Optional[str] = ..., event_ts: _Optional[float] = ..., event_source: _Optional[str] = ..., opaque_params: _Optional[str] = ..., eave_account_id: _Optional[str] = ..., eave_visitor_id: _Optional[str] = ..., eave_team_id: _Optional[str] = ..., eave_env: _Optional[str] = ...) -> None: ...
