from dataclasses import dataclass
from typing import Optional

import pydantic


@dataclass
class OAuthFlowInfo:
    authorization_url: str
    state: str


class OAuthCallbackRequestBody(pydantic.BaseModel):
    state: Optional[str]
    code: Optional[str]
    error: Optional[str]
