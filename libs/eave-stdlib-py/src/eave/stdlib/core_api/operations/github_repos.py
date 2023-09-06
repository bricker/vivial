from typing import Unpack
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

# TODO: should all these be authed???/


class GetGithubReposRequest(Endpoint):
    config = EndpointConfiguration(
        path="/github-repos/query",
        auth_required=False,
    )

    class RequestBody(BaseRequestBody):
        repos: GithubRepoListInput

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


class FeatureStateGithubReposRequest(Endpoint):
    config = EndpointConfiguration(
        path="/github-repos/query/enabled",
        auth_required=False,
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
        auth_required=False,
    )

    class RequestBody(BaseRequestBody):
        repo: GithubRepoCreateInput

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


class UpdateGithubReposRequest(Endpoint):
    config = EndpointConfiguration(
        path="/github-repos/update",
        auth_required=False,
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
