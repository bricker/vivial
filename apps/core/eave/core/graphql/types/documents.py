from typing import Optional

import strawberry
from eave.stdlib.core_api.models import BaseResponseModel
from eave.stdlib.core_api.models import BaseInputModel

@strawberry.type
class DocumentSearchResult:
    title: str
    url: Optional[str]

@strawberry.input
class DocumentInput:
    title: str
    content: str
    parent: Optional["DocumentInput"] = None
