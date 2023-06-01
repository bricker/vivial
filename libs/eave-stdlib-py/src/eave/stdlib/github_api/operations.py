from typing import Optional
import pydantic

from ..core_api.models.subscriptions import Subscription


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
