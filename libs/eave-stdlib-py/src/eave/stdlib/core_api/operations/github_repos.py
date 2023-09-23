from typing import Unpack, Optional
import uuid
from ... import requests
from eave.stdlib.core_api.models.github_repos import (
    GithubRepo,
    GithubRepoCreateInput,
    GithubRepoListInput,
    GithubReposDeleteInput,
    GithubRepoUpdateInput,
    GithubReposFeatureStateInput,
)
from . import BaseRequestBody, BaseResponseBody, Endpoint, EndpointConfiguration


class GetGithubReposRequest(Endpoint):
    config = EndpointConfiguration(
        path="/github-repos/query",
    )

    class RequestBody(BaseRequestBody):
        repos: Optional[list[GithubRepoListInput]] = None

    class ResponseBody(BaseResponseBody):
        repos: list[GithubRepo]

    @classmethod
    async def perform(
        cls,
        team_id: uuid.UUID | str,
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


class FeatureStateGithubReposRequest(Endpoint):
    config = EndpointConfiguration(
        path="/github-repos/query/enabled",
    )

    class RequestBody(BaseRequestBody):
        query_params: GithubReposFeatureStateInput

    class ResponseBody(BaseResponseBody):
        states_match: bool

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
    )

    class RequestBody(BaseRequestBody):
        repo: GithubRepoCreateInput

    class ResponseBody(BaseResponseBody):
        repo: GithubRepo

    @classmethod
    async def perform(
        cls,
        input: RequestBody,
        team_id: uuid.UUID | str,
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
    )

    class RequestBody(BaseRequestBody):
        repos: list[GithubReposDeleteInput]

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


class UpdateGithubReposRequest(Endpoint):
    config = EndpointConfiguration(
        path="/github-repos/update",
    )

    class RequestBody(BaseRequestBody):
        repos: list[GithubRepoUpdateInput]

    class ResponseBody(BaseResponseBody):
        repos: list[GithubRepo]

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
