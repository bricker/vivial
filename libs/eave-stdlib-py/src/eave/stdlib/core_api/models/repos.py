import enum
from typing import Optional
import uuid

from pydantic import BaseModel
from eave.stdlib.core_api.models import BaseResponseModel

from eave.stdlib.core_api.models import BaseInputModel

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