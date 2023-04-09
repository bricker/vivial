from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class EaveUserAction(_message.Message):
    __slots__ = ["action", "message_source"]
    class Action(_message.Message):
        __slots__ = ["description", "eave_user_id", "name", "opaque_params", "platform", "user_ts"]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        EAVE_USER_ID_FIELD_NUMBER: _ClassVar[int]
        NAME_FIELD_NUMBER: _ClassVar[int]
        OPAQUE_PARAMS_FIELD_NUMBER: _ClassVar[int]
        PLATFORM_FIELD_NUMBER: _ClassVar[int]
        USER_TS_FIELD_NUMBER: _ClassVar[int]
        description: str
        eave_user_id: str
        name: str
        opaque_params: str
        platform: str
        user_ts: int
        def __init__(self, platform: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., opaque_params: _Optional[str] = ..., eave_user_id: _Optional[str] = ..., user_ts: _Optional[int] = ...) -> None: ...
    ACTION_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_SOURCE_FIELD_NUMBER: _ClassVar[int]
    action: EaveUserAction.Action
    message_source: str
    def __init__(self, action: _Optional[_Union[EaveUserAction.Action, _Mapping]] = ..., message_source: _Optional[str] = ...) -> None: ...
