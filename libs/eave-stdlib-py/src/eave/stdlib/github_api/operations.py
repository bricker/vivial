from typing import Optional
import pydantic


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
