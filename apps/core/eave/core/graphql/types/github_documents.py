import datetime
from enum import StrEnum
from typing import Optional
import uuid

import strawberry

from eave.stdlib.core_api.models import BaseResponseModel
from eave.stdlib.core_api.models import BaseInputModel

@strawberry.enum
class Status(StrEnum):
    PROCESSING = "processing"
    PR_OPENED = "pr_opened"
    PR_MERGED = "pr_merged"

@strawberry.enum
class DocumentType(StrEnum):
    API_DOCUMENT = "api_document"
    ARCHITECTURE_DOCUMENT = "architecture_document"

@strawberry.type
class GithubDocument:
    id: uuid.UUID
    team_id: uuid.UUID
    external_repo_id: str
    pull_request_number: Optional[int]
    status: Status
    status_updated: datetime.datetime
    file_path: Optional[str]
    api_name: Optional[str]
    type: DocumentType

@strawberry.input
class GithubDocumentsQueryInput:
    id: Optional[uuid.UUID] = None
    external_repo_id: Optional[str] = None
    type: Optional[DocumentType] = None

@strawberry.input
class GithubDocumentCreateInput:
    external_repo_id: str
    type: DocumentType
    file_path: Optional[str] = None
    api_name: Optional[str] = None
    pull_request_number: Optional[int] = None

@strawberry.input
class GithubDocumentValuesInput:
    pull_request_number: Optional[int] = None
    status: Optional[Status] = None
    file_path: Optional[str] = None
    api_name: Optional[str] = None

@strawberry.input
class GithubDocumentUpdateInput:
    id: uuid.UUID
    new_values: GithubDocumentValuesInput

@strawberry.input
class GithubDocumentsDeleteByIdsInput:
    id: uuid.UUID

@strawberry.input
class GithubDocumentsDeleteByTypeInput:
    type: DocumentType
