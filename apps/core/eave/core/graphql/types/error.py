from typing import Optional

import strawberry.federation as sb

from eave.stdlib.typing import JsonObject


@sb.type
class ErrorResponse:
    status_code: int = sb.field()
    error_message: str = sb.field()
    context: Optional[JsonObject] = sb.field()
