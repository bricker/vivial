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
from . import BaseRequestBody, BaseResponseBody, CoreApiEndpoint, CoreApiEndpointConfiguration


class GetGithubReposRequest(CoreApiEndpoint):
    config = CoreApiEndpointConfiguration(
        path="/github-repos/query",
        auth_required=False,
    )

    class RequestBody(BaseRequestBody):
        repos: Optional[list[GithubRepoListInput]] = None

    class ResponseBody(BaseResponseBody):
        repos: list[GithubRepo]

    @classmethod
    async def perform(
        cls,
        input: RequestBody,
        team_id: uuid.UUID | str,
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


class GetAllTeamsGithubReposRequest(CoreApiEndpoint):
    config = CoreApiEndpointConfiguration(path="/_/github-repos/query", auth_required=False, team_id_required=False)

    class RequestBody(BaseRequestBody):
        query_params: GithubReposFeatureStateInput

    class ResponseBody(BaseResponseBody):
        repos: list[GithubRepo]

    @classmethod
    async def perform(
        cls,
        input: RequestBody,
        **kwargs: Unpack[requests.CommonRequestArgs],
    ) -> ResponseBody:
        response = await requests.make_request(
            config=cls.config,
            input=input,
            **kwargs,
        )

        response_json = await response.json()
        return cls.ResponseBody(**response_json, _raw_response=response)


class FeatureStateGithubReposRequest(CoreApiEndpoint):
    config = CoreApiEndpointConfiguration(
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
        team_id: uuid.UUID | str,
        **kwargs: Unpack[requests.CommonRequestArgs],
    ) -> ResponseBody:
        response = await requests.make_request(
            config=cls.config,
            input=None,
            team_id=team_id,
            **kwargs,
        )

        response_json = await response.json()
        return cls.ResponseBody(**response_json, _raw_response=response)


class CreateGithubRepoRequest(CoreApiEndpoint):
    config = CoreApiEndpointConfiguration(
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
        team_id: uuid.UUID | str,
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


class DeleteGithubReposRequest(CoreApiEndpoint):
    config = CoreApiEndpointConfiguration(
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
        team_id: uuid.UUID | str,
        account_id: uuid.UUID | str,
        access_token: str,
        **kwargs: Unpack[requests.CommonRequestArgs],
    ) -> ResponseBody:
        response = await requests.make_request(
            config=cls.config,
            input=input,
            team_id=team_id,
            account_id=account_id,
            access_token=access_token,
            **kwargs,
        )

        return cls.ResponseBody(_raw_response=response)


class UpdateGithubReposRequest(CoreApiEndpoint):
    config = CoreApiEndpointConfiguration(
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
        team_id: uuid.UUID | str,
        account_id: uuid.UUID | str,
        access_token: str,
        **kwargs: Unpack[requests.CommonRequestArgs],
    ) -> ResponseBody:
        response = await requests.make_request(
            config=cls.config,
            input=input,
            team_id=team_id,
            account_id=account_id,
            access_token=access_token,
            **kwargs,
        )

        response_json = await response.json()
        return cls.ResponseBody(**response_json, _raw_response=response)
