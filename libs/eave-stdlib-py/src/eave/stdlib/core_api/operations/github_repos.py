from typing import Unpack
import uuid
from ... import requests
from eave.stdlib.core_api.models.github_repos import GithubRepo, GithubRepoInput, GithubReposDeleteInput, GithubRepoUpdateInput
from . import BaseRequestBody, BaseResponseBody, Endpoint, EndpointConfiguration

# TODO: should all these be authed???/


class GetGithubRepoRequest(Endpoint):
    config = EndpointConfiguration(
        path="/github-repos/query",
        auth_required=False,
    )

    class RequestBody(BaseRequestBody):
        repo: GithubRepoInput

    class ResponseBody(BaseResponseBody):
        repo: GithubRepo

    @classmethod
    async def perform(
        cls,
        input: RequestBody,
        team_id: uuid.UUID,
        **kwargs: Unpack[requests.CommonRequestArgs],
    ) -> ResponseBody:
        response = await requests.make_request(
            url=cls.config.url,
            input=input,
            team_id=team_id,
            **kwargs,
        )

        response_json = await response.json()
        return cls.ResponseBody(**response_json, _raw_response=response)


class ListGithubReposRequest(Endpoint):
    config = EndpointConfiguration(
        path="/github-repos/query/list",
        auth_required=False,
    )

    class ResponseBody(BaseResponseBody):
        repos: list[GithubRepo]

    @classmethod
    async def perform(
        cls,
        team_id: uuid.UUID,
        **kwargs: Unpack[requests.CommonRequestArgs],
    ) -> ResponseBody:
        response = await requests.make_request(
            url=cls.config.url,
            input=None,
            team_id=team_id,
            **kwargs,
        )

        response_json = await response.json()
        return cls.ResponseBody(**response_json, _raw_response=response)


class CreateGithubRepoRequest(Endpoint):
    config = EndpointConfiguration(
        path="/github-repos/create",
        auth_required=False,
    )

    class RequestBody(BaseRequestBody):
        repo: GithubRepoInput

    class ResponseBody(BaseResponseBody):
        repo: GithubRepo

    @classmethod
    async def perform(
        cls,
        input: RequestBody,
        team_id: uuid.UUID,
        **kwargs: Unpack[requests.CommonRequestArgs],
    ) -> ResponseBody:
        response = await requests.make_request(
            url=cls.config.url,
            input=input,
            team_id=team_id,
            **kwargs,
        )

        response_json = await response.json()
        return cls.ResponseBody(**response_json, _raw_response=response)


class DeleteGithubReposRequest(Endpoint):
    config = EndpointConfiguration(
        path="/github-repos/delete",
        auth_required=False,
    )

    class RequestBody(BaseRequestBody):
        repos: GithubReposDeleteInput

    class ResponseBody(BaseResponseBody):
        pass

    @classmethod
    async def perform(
        cls,
        input: RequestBody,
        team_id: uuid.UUID,
        **kwargs: Unpack[requests.CommonRequestArgs],
    ) -> ResponseBody:
        response = await requests.make_request(
            url=cls.config.url,
            input=input,
            team_id=team_id,
            **kwargs,
        )

        return cls.ResponseBody(_raw_response=response)

class UpdateGithubRepoRequest(Endpoint):
    config = EndpointConfiguration(
        path="/github-repos/update",
        auth_required=False,
    )

    class RequestBody(BaseRequestBody):
        repo: GithubRepoUpdateInput

    class ResponseBody(BaseResponseBody):
        repo: GithubRepo

    @classmethod
    async def perform(
        cls,
        input: RequestBody,
        team_id: uuid.UUID,
        **kwargs: Unpack[requests.CommonRequestArgs],
    ) -> ResponseBody:
        response = await requests.make_request(
            url=cls.config.url,
            input=input,
            team_id=team_id,
            **kwargs,
        )

        response_json = await response.json()
        return cls.ResponseBody(**response_json, _raw_response=response)

