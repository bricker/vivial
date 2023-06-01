from typing import Optional
from eave.stdlib.core_api.models import BaseResponseModel
from eave.stdlib.core_api.models import BaseInputModel


class DocumentSearchResult(BaseResponseModel):
    title: str
    url: str


class DocumentInput(BaseInputModel):
    title: str
    content: str
    parent: Optional["DocumentInput"] = None