from typing import Optional, Unpack
import uuid
from eave.stdlib import requests
from eave.stdlib.api_types import BaseRequestBody, BaseResponseBody
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
        return await requests.make_request(
            config=cls.config,
            response_type=cls.ResponseBody,
            input=input,
            team_id=team_id,
            **kwargs,
        )
