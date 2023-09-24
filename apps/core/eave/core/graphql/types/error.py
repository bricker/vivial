from typing import Optional

import strawberry

from . import BaseResponseModel
from ... import typing


@strawberry.type
class ErrorResponse:
    status_code: int
    error_message: str
    context: Optional[typing.JsonObject]
