import datetime
from enum import StrEnum

from eave.stdlib.core_api.models import BaseResponseModel
from typing import Optional
import uuid
from pydantic import BaseModel

from eave.stdlib.core_api.models import BaseResponseModel
from eave.stdlib.core_api.models import BaseInputModel


class Status(StrEnum):
    PROCESSING = "processing"
    PR_OPENED = "pr_opened"
    PR_MERGED = "pr_merged"


class DocumentType(StrEnum):
    API_DOCUMENT = "api_document"
    ARCHITECTURE_DOCUMENT = "architecture_document"


class GithubDocument(BaseResponseModel):
    team_id: uuid.UUID
    external_repo_id: str
    pull_request_number: int
    status: Status
    status_updated: Optional[datetime.datetime]
    file_path: str
    api_name: str
    type: DocumentType
