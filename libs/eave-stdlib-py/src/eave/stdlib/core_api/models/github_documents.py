import datetime
from enum import StrEnum
from typing import Optional
import uuid

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
    id: uuid.UUID
    team_id: uuid.UUID
    external_repo_id: str
    pull_request_number: Optional[int]
    status: Status
    status_updated: datetime.datetime
    file_path: Optional[str]
    api_name: Optional[str]
    type: DocumentType


class GithubDocumentsQueryInput(BaseInputModel):
    id: Optional[uuid.UUID] = None
    external_repo_id: Optional[str] = None
    type: Optional[DocumentType] = None


class GithubDocumentCreateInput(BaseInputModel):
    external_repo_id: str
    type: DocumentType
    file_path: Optional[str] = None
    api_name: Optional[str] = None
    pull_request_number: Optional[int] = None


class GithubDocumentValuesInput(BaseInputModel):
    pull_request_number: Optional[int] = None
    status: Optional[Status] = None
    file_path: Optional[str] = None
    api_name: Optional[str] = None


class GithubDocumentUpdateInput(BaseInputModel):
    id: uuid.UUID
    new_values: GithubDocumentValuesInput


class GithubDocumentsDeleteByIdsInput(BaseInputModel):
    id: uuid.UUID


class GithubDocumentsDeleteByTypeInput(BaseInputModel):
    type: DocumentType
