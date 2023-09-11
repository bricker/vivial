import enum
from typing import Optional
import uuid

from eave.stdlib.core_api.models import BaseResponseModel

from eave.stdlib.core_api.models import BaseInputModel


class Feature(enum.StrEnum):
    API_DOCUMENTATION = "api_documentation"
    INLINE_CODE_DOCUMENTATION = "inline_code_documentation"
    ARCHITECTURE_DOCUMENTATION = "architecture_documentation"


class State(enum.StrEnum):
    DISABLED = "disabled"
    ENABLED = "enabled"
    PAUSED = "paused"


class GithubRepo(BaseResponseModel):
    team_id: uuid.UUID
    external_repo_id: str
    api_documentation_state: State
    inline_code_documentation_state: State
    architecture_documentation_state: State


class GithubRepoCreateInput(BaseInputModel):
    external_repo_id: str
    api_documentation_state: State = State.DISABLED
    inline_code_documentation_state: State = State.DISABLED
    architecture_documentation_state: State = State.DISABLED


class GithubRepoListInput(BaseInputModel):
    external_repo_id: str


class GithubRepoUpdateValues(BaseInputModel):
    api_documentation_state: Optional[State] = None
    inline_code_documentation_state: Optional[State] = None
    architecture_documentation_state: Optional[State] = None


class GithubRepoUpdateInput(BaseInputModel):
    external_repo_id: str
    new_values: GithubRepoUpdateValues


class GithubReposDeleteInput(BaseInputModel):
    external_repo_ids: list[str]


class GithubReposFeatureStateInput(BaseInputModel):
    feature: Feature
    state: State
