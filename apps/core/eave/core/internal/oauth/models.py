from dataclasses import dataclass

import pydantic


@dataclass
class OAuthFlowInfo:
    authorization_url: str
    state: str


class OAuthCallbackRequestBody(pydantic.BaseModel):
    state: str | None
    code: str | None
    error: str | None
