from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class GPTRequestEvent(_message.Message):
    __slots__ = ["duration_seconds", "eave_request_id", "eave_team_id", "event_time", "feature_name", "input_cost_usd", "input_prompt", "input_token_count", "model", "output_cost_usd", "output_response", "output_token_count"]
    DURATION_SECONDS_FIELD_NUMBER: _ClassVar[int]
    EAVE_REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    EAVE_TEAM_ID_FIELD_NUMBER: _ClassVar[int]
    EVENT_TIME_FIELD_NUMBER: _ClassVar[int]
    FEATURE_NAME_FIELD_NUMBER: _ClassVar[int]
    INPUT_COST_USD_FIELD_NUMBER: _ClassVar[int]
    INPUT_PROMPT_FIELD_NUMBER: _ClassVar[int]
    INPUT_TOKEN_COUNT_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_COST_USD_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_TOKEN_COUNT_FIELD_NUMBER: _ClassVar[int]
    duration_seconds: int
    eave_request_id: str
    eave_team_id: str
    event_time: str
    feature_name: str
    input_cost_usd: float
    input_prompt: str
    input_token_count: int
    model: str
    output_cost_usd: float
    output_response: str
    output_token_count: int
    def __init__(self, feature_name: _Optional[str] = ..., event_time: _Optional[str] = ..., duration_seconds: _Optional[int] = ..., eave_request_id: _Optional[str] = ..., input_cost_usd: _Optional[float] = ..., output_cost_usd: _Optional[float] = ..., input_prompt: _Optional[str] = ..., output_response: _Optional[str] = ..., input_token_count: _Optional[int] = ..., output_token_count: _Optional[int] = ..., model: _Optional[str] = ..., eave_team_id: _Optional[str] = ...) -> None: ...
