from typing import Unpack
import uuid
from eave.stdlib import requests
from eave.stdlib.core_api.operations import BaseResponseBody
from eave.stdlib.github_api.models import ExternalGithubRepo
from eave.stdlib.github_api.operations import GithubAppEndpoint, GithubAppEndpointConfiguration


class QueryGithubRepos(GithubAppEndpoint):
    config = GithubAppEndpointConfiguration(
        path="/github/api/repos/query",
    )

    class ResponseBody(BaseResponseBody):
        repos: list[ExternalGithubRepo]

    @classmethod
    async def perform(cls, team_id: uuid.UUID, **kwargs: Unpack[requests.CommonRequestArgs]) -> ResponseBody:
        response = await requests.make_request(
            config=cls.config,
            input=None,
            team_id=team_id,
            **kwargs,
        )

        response_json = await response.json()
        return cls.ResponseBody(**response_json, _raw_response=response)
