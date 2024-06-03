import uuid

from eave.stdlib.core_api.models import BaseInputModel, BaseResponseModel
from google.cloud.bigquery import SqlTypeNames

from eave.core.internal.atoms.table_handle import BigQueryFieldMode

class VirtualEventField(BaseResponseModel):
    name: str
    description: str
    type: SqlTypeNames
    mode: BigQueryFieldMode
    fields: list["VirtualEventField"] | None = None

class VirtualEventPeek(BaseResponseModel):
    id: uuid.UUID
    view_id: str
    readable_name: str
    description: str | None

class VirtualEventDetails(BaseResponseModel):
    id: uuid.UUID
    view_id: str
    readable_name: str
    description: str | None
    fields: list[VirtualEventField]

class VirtualEventQueryInput(BaseInputModel):
    search_term: str
