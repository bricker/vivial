import enum
from typing import Optional
import uuid

from eave.stdlib.core_api.models import BaseResponseModel

from eave.stdlib.core_api.models import BaseInputModel


class GithubRepoFeature(enum.StrEnum):
    API_DOCUMENTATION = "api_documentation"
    INLINE_CODE_DOCUMENTATION = "inline_code_documentation"
    ARCHITECTURE_DOCUMENTATION = "architecture_documentation"


class GibhuRepoFeatureState(enum.StrEnum):
    DISABLED = "disabled"
    ENABLED = "enabled"
    PAUSED = "paused"


class GithubRepo(BaseResponseModel):
    team_id: uuid.UUID
    id: uuid.UUID
    github_installation_id: uuid.UUID
    external_repo_id: str
    display_name: Optional[str]
    api_documentation_state: GibhuRepoFeatureState
    inline_code_documentation_state: GibhuRepoFeatureState
    architecture_documentation_state: GibhuRepoFeatureState


class GithubRepoCreateInput(BaseInputModel):
    external_repo_id: str
    display_name: str
    api_documentation_state: Optional[GibhuRepoFeatureState] = None
    inline_code_documentation_state: Optional[GibhuRepoFeatureState] = None
    architecture_documentation_state: Optional[GibhuRepoFeatureState] = None


class GithubRepoRefInput(BaseInputModel):
    id: uuid.UUID


class GithubRepoListInput(BaseInputModel):
    external_repo_id: str


class GithubRepoUpdateValues(BaseInputModel):
    api_documentation_state: Optional[GibhuRepoFeatureState] = None
    inline_code_documentation_state: Optional[GibhuRepoFeatureState] = None
    architecture_documentation_state: Optional[GibhuRepoFeatureState] = None


class GithubRepoUpdateInput(BaseInputModel):
    id: uuid.UUID
    new_values: GithubRepoUpdateValues


class GithubReposDeleteInput(BaseInputModel):
    id: uuid.UUID


class GithubReposFeatureStateInput(BaseInputModel):
    feature: GithubRepoFeature
    state: GibhuRepoFeatureState
