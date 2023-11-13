from enum import StrEnum
from typing import Optional
from uuid import UUID
from eave.stdlib.core_api.models import BaseResponseModel
from eave.stdlib.core_api.models import BaseInputModel


class ApiDocumentationJob(BaseResponseModel):
    id: UUID
    team_id: UUID
    github_repo_id: UUID
    """foreign key to github_repos.id"""
    state: str
    last_result: str


class LastJobResult(StrEnum):
    none = "none"
    doc_created = "doc_created"
    no_api_found = "no_api_found"
    error = "error"


class ApiDocumentationJobState(StrEnum):
    running = "running"
    idle = "idle"


class ApiDocumentationJobListInput(BaseInputModel):
    id: UUID


class ApiDocumentationJobUpsertInput(BaseInputModel):
    github_repo_id: UUID
    state: ApiDocumentationJobState
    last_result: Optional[LastJobResult] = None  # TODO: does this need to be option?
