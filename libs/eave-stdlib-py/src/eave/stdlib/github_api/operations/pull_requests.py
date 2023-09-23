from typing import Unpack
import uuid

from eave.stdlib import requests
from eave.stdlib.core_api.operations import BaseRequestBody, BaseResponseBody
from eave.stdlib.github_api.operations import GithubAppEndpoint, GithubAppEndpointConfiguration
from ..models import FileChange


class CreateGitHubPullRequest(GithubAppEndpoint):
    config = GithubAppEndpointConfiguration(
        path="/github/api/create-pull-request",
    )

    class RequestBody(BaseRequestBody):
        repo_name: str
        repo_owner: str
        repo_id: str
        base_branch_name: str
        branch_name: str
        commit_message: str
        pr_title: str
        pr_body: str
        file_changes: list[FileChange]

    class ResponseBody(BaseResponseBody):
        pr_number: int

    @classmethod
    async def perform(
        cls,
        team_id: uuid.UUID,
        input: RequestBody,
        **kwargs: Unpack[requests.CommonRequestArgs],
    ) -> ResponseBody:
        response = await requests.make_request(
            config=cls.config,
            input=input,
            team_id=team_id,
            **kwargs,
        )

        response_json = await response.json()
        return cls.ResponseBody(**response_json, _raw_response=response)
