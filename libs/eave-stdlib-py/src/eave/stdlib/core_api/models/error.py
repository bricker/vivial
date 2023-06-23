from typing import Optional

from . import BaseResponseModel
from ... import typing


class ErrorResponse(BaseResponseModel):
    status_code: int
    error_message: str
    context: Optional[typing.JsonObject]
