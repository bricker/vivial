from typing import Unpack
import uuid
from eave.stdlib import requests
from eave.stdlib.api_types import BaseResponseBody
from eave.stdlib.github_api.models import ExternalGithubRepo
from eave.stdlib.github_api.operations import GithubAppEndpoint, GithubAppEndpointConfiguration


class QueryGithubRepos(GithubAppEndpoint):
    config = GithubAppEndpointConfiguration(
        path="/github/api/repos/query",
    )

    class ResponseBody(BaseResponseBody):
        repos: list[ExternalGithubRepo]

    @classmethod
    async def perform(cls, team_id: uuid.UUID | str, **kwargs: Unpack[requests.CommonRequestArgs]) -> ResponseBody:
        return await requests.make_request(
            config=cls.config,
            response_type=cls.ResponseBody,
            input=None,
            team_id=team_id,
            **kwargs,
        )
