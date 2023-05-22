from typing import Optional
import pydantic
from eave.stdlib.core_api.models import Subscription


class Endpoint:
    pass


class GetGithubUrlContent(Endpoint):
    class RequestBody(pydantic.BaseModel):
        url: str

    class ResponseBody(pydantic.BaseModel):
        content: Optional[str]


class CreateGithubResourceSubscription(Endpoint):
    class RequestBody(pydantic.BaseModel):
        url: str

    class ResponseBody(pydantic.BaseModel):
        subscription: Optional[Subscription]
