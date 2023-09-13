import enum
import uuid

from eave.stdlib.core_api.models import BaseResponseModel


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
    api_documentation_state: State = State.DISABLED
    inline_code_documentation_state: State = State.DISABLED
    architecture_documentation_state: State = State.DISABLED
