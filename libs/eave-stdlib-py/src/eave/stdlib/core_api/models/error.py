from typing import Optional

from . import BaseResponseModel
from ...typing import JsonObject


class ErrorResponse(BaseResponseModel):
    status_code: int
    error_message: str
    context: Optional[JsonObject]
