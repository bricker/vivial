import uuid
from typing import Unpack

from eave.stdlib.core_api.models.github_installation import GithubInstallation, GithubInstallationQueryInput
from eave.stdlib.core_api.models.team import Team, TeamQueryInput
from eave.stdlib.endpoints import BaseRequestBody, BaseResponseBody

from ... import requests_util
from . import CoreApiEndpoint, CoreApiEndpointConfiguration


class QueryGithubInstallation(CoreApiEndpoint):
    config = CoreApiEndpointConfiguration(
        path="/_/github_installations/query",
        signature_required=False,
        auth_required=False,
        team_id_required=False,
    )

    class RequestBody(BaseRequestBody):
        team: TeamQueryInput | None = None
        github_installation: GithubInstallationQueryInput | None = None

    class ResponseBody(BaseResponseBody):
        team: Team | None
        github_installation: GithubInstallation

    @classmethod
    async def perform(
        cls,
        input: RequestBody,
        **kwargs: Unpack[requests_util.CommonRequestArgs],
    ) -> ResponseBody:
        response = await requests_util.make_request(
            config=cls.config,
            input=input,
            **kwargs,
        )

        body = await cls.make_response(response, cls.ResponseBody)
        return body


class DeleteGithubInstallation(CoreApiEndpoint):
    config = CoreApiEndpointConfiguration(
        path="/_/github_installations/delete",
        auth_required=False,
        signature_required=False,
    )

    class RequestBody(BaseRequestBody):
        github_installation: GithubInstallationQueryInput

    class ResponseBody(BaseResponseBody):
        pass

    @classmethod
    async def perform(
        cls,
        input: RequestBody,
        team_id: uuid.UUID,
        **kwargs: Unpack[requests_util.CommonRequestArgs],
    ) -> ResponseBody:
        response = await requests_util.make_request(
            config=cls.config,
            input=input,
            team_id=team_id,
            **kwargs,
        )

        body = await cls.make_response(response, cls.ResponseBody)
        return body
