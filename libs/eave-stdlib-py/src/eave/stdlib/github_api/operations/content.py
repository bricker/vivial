from typing import Optional, Unpack
import uuid
from eave.stdlib import requests
from eave.stdlib.core_api.operations import BaseRequestBody, BaseResponseBody
from eave.stdlib.github_api.operations import GithubAppEndpoint, GithubAppEndpointConfiguration


class GetGithubUrlContent(GithubAppEndpoint):
    config = GithubAppEndpointConfiguration(
        path="/github/api/content",
    )

    class RequestBody(BaseRequestBody):
        url: str

    class ResponseBody(BaseResponseBody):
        content: Optional[str]

    @classmethod
    async def perform(
        cls, input: RequestBody, team_id: uuid.UUID, **kwargs: Unpack[requests.CommonRequestArgs]
    ) -> ResponseBody:
        response = await requests.make_request(
            url=cls.config.url,
            input=input,
            team_id=team_id,
            **kwargs,
        )

        response_json = await response.json()
        return cls.ResponseBody(**response_json, _raw_response=response)
