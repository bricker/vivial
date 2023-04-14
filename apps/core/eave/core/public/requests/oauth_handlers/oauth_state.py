from dataclasses import dataclass
from typing import Optional

import pydantic

@dataclass
class OauthFlowInfo:
    authorization_url: str
    state: str

class OauthCallbackRequestBody(pydantic.BaseModel):
    state: Optional[str]
    code: Optional[str]
    error: Optional[str]
