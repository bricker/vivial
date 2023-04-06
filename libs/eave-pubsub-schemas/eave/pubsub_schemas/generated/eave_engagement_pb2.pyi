from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class EaveEngagement(_message.Message):
    __slots__ = ["client_ts", "content", "eave_team_id", "eave_user_id"]
    CLIENT_TS_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    EAVE_TEAM_ID_FIELD_NUMBER: _ClassVar[int]
    EAVE_USER_ID_FIELD_NUMBER: _ClassVar[int]
    client_ts: int
    content: str
    eave_team_id: str
    eave_user_id: str
    def __init__(self, content: _Optional[str] = ..., eave_user_id: _Optional[str] = ..., eave_team_id: _Optional[str] = ..., client_ts: _Optional[int] = ...) -> None: ...
