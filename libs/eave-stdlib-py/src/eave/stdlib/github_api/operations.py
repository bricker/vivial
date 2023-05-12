from typing import Optional
import pydantic
import uuid
from eave.stdlib.core_api.models import Subscription


class Endpoint:
    pass


class GetGithubUrlContent(Endpoint):
    class RequestBody(pydantic.BaseModel):
        eave_team_id: uuid.UUID
        url: str

    class ResponseBody(pydantic.BaseModel):
        content: Optional[str]


class CreateGithubResourceSubscription(Endpoint):
    class RequestBody(pydantic.BaseModel):
        eave_team_id: uuid.UUID
        url: str

    class ResponseBody(pydantic.BaseModel):
        subscription: Optional[Subscription]
