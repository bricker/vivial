from typing import Optional, Unpack
import uuid
import aiohttp
import pydantic
from eave.stdlib import requests
from eave.stdlib.core_api.models.subscriptions import DocumentReference, Subscription
from eave.stdlib.core_api.models.team import Team
from eave.stdlib.eave_origins import EaveApp
from ..config import shared_config

from eave.stdlib.github_api.models import GithubRepoInput

_base_url = shared_config.eave_internal_service_base(EaveApp.eave_github_app)


class Endpoint:
    pass


class BaseRequestBody(pydantic.BaseModel):
    pass


class BaseResponseBody(pydantic.BaseModel):
    _raw_response: Optional[aiohttp.ClientResponse] = None

    class Config:
        underscore_attrs_are_private = True


class GetGithubUrlContent(Endpoint):
    class RequestBody(BaseRequestBody):
        url: str

    class ResponseBody(BaseResponseBody):
        content: Optional[str]

    @classmethod
    async def perform(
        cls, input: RequestBody, team_id: uuid.UUID, **kwargs: Unpack[requests.CommonRequestArgs]
    ) -> ResponseBody:
        response = await requests.make_request(
            url=f"{_base_url}/github/api/content",
            input=input,
            team_id=team_id,
            **kwargs,
        )

        response_json = await response.json()
        return cls.ResponseBody(**response_json, _raw_response=response)


class CreateGithubResourceSubscription(Endpoint):
    class RequestBody(BaseRequestBody):
        url: str

    class ResponseBody(BaseResponseBody):
        team: Team
        subscription: Subscription
        document_reference: Optional[DocumentReference] = None

    @classmethod
    async def perform(
        cls, input: RequestBody, team_id: uuid.UUID, **kwargs: Unpack[requests.CommonRequestArgs]
    ) -> ResponseBody:
        response = await requests.make_request(
            url=f"{_base_url}/github/api/subscribe",
            input=input,
            team_id=team_id,
            **kwargs,
        )

        response_json = await response.json()
        return cls.ResponseBody(**response_json, _raw_response=response)


class RunApiDocumentationTask(Endpoint):
    class RequestBody(BaseRequestBody):
        repo: GithubRepoInput

    class ResponseBody(BaseResponseBody):
        pass

    @classmethod
    async def perform(
        cls, input: RequestBody, team_id: uuid.UUID, **kwargs: Unpack[requests.CommonRequestArgs]
    ) -> ResponseBody:
        response = await requests.make_request(
            url=f"{_base_url}/_/github/run-api-documentation",
            input=input,
            team_id=team_id,
            **kwargs,
        )

        response_json = await response.json()
        return cls.ResponseBody(**response_json, _raw_response=response)
