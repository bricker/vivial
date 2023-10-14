from typing import Unpack
import uuid
from eave.stdlib import requests
from eave.stdlib.core_api.operations import BaseRequestBody, BaseResponseBody

from eave.stdlib.github_api.models import GithubRepoInput
from eave.stdlib.github_api.operations import GithubAppEndpoint, GithubAppEndpointConfiguration


class RunApiDocumentationTask(GithubAppEndpoint):
    config = GithubAppEndpointConfiguration(
        path="/_/github/tasks/run-api-documentation",
    )

    class RequestBody(BaseRequestBody):
        repo: GithubRepoInput

    class ResponseBody(BaseResponseBody):
        pass

    @classmethod
    async def perform(
        cls, input: RequestBody, team_id: uuid.UUID, **kwargs: Unpack[requests.CommonRequestArgs]
    ) -> ResponseBody:
        response = await requests.make_request(
            config=cls.config,
            input=input,
            team_id=team_id,
            **kwargs,
        )

        body = await cls.make_response(response, cls.ResponseBody)
        return body
