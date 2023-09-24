import enum
from typing import Optional
import uuid

import strawberry

from eave.stdlib.core_api.models import BaseResponseModel

from eave.stdlib.core_api.models import BaseInputModel

@strawberry.enum
class Feature(enum.StrEnum):
    API_DOCUMENTATION = "api_documentation"
    INLINE_CODE_DOCUMENTATION = "inline_code_documentation"
    ARCHITECTURE_DOCUMENTATION = "architecture_documentation"

@strawberry.enum
class State(enum.StrEnum):
    DISABLED = "disabled"
    ENABLED = "enabled"
    PAUSED = "paused"

@strawberry.type
class GithubRepo:
    team_id: uuid.UUID
    external_repo_id: str
    display_name: Optional[str]
    api_documentation_state: State
    inline_code_documentation_state: State
    architecture_documentation_state: State

@strawberry.input
class GithubRepoCreateInput:
    external_repo_id: str
    display_name: str
    api_documentation_state: State = State.DISABLED
    inline_code_documentation_state: State = State.DISABLED
    architecture_documentation_state: State = State.DISABLED

@strawberry.input
class GithubRepoListInput:
    external_repo_id: str

@strawberry.input
class GithubRepoUpdateValues:
    api_documentation_state: Optional[State] = None
    inline_code_documentation_state: Optional[State] = None
    architecture_documentation_state: Optional[State] = None

@strawberry.input
class GithubRepoUpdateInput:
    external_repo_id: str
    new_values: GithubRepoUpdateValues

@strawberry.input
class GithubReposDeleteInput:
    external_repo_id: str

@strawberry.input
class GithubReposFeatureStateInput:
    feature: Feature
    state: State
