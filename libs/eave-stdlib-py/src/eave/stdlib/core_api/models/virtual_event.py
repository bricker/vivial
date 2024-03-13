import uuid

from eave.stdlib.core_api.models import BaseInputModel, BaseResponseModel

from typing import Optional

# TODO: need access to list of fields; but that's not in the ORM yet
class VirtualEvent(BaseResponseModel):
    id: uuid.UUID
    readable_name: str
    description: Optional[str]

class VirtualEventQueryInput(BaseInputModel):
    search_term: str
