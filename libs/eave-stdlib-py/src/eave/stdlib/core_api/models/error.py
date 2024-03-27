from typing import Optional

from ... import typing
from . import BaseResponseModel


class ErrorResponse(BaseResponseModel):
    status_code: int
    error_message: str
    context: Optional[typing.JsonObject]
