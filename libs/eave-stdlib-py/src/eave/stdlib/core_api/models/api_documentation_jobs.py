from enum import StrEnum
from typing import Optional
from uuid import UUID
from eave.stdlib.core_api.models import BaseResponseModel
from eave.stdlib.core_api.models import BaseInputModel

class ApiDocumentationJob(BaseResponseModel):
    id: UUID
    team_id: UUID

class LastJobResult(StrEnum):
    none = "none"
    doc_created = "doc_created"
    no_api_found = "no_api_found"
    error = "error"

class ApiDocumentationJobState(StrEnum):
    running = "running"
    idle = "idle"