import uuid
from typing import Optional, Unpack

from eave.stdlib.core_api.models.github_installation import GithubInstallation, GithubInstallationQueryInput
from eave.stdlib.core_api.models.team import Team, TeamQueryInput
from eave.stdlib.endpoints import BaseRequestBody, BaseResponseBody

from ... import requests
from . import CoreApiEndpoint, CoreApiEndpointConfiguration


class QueryGithubInstallation(CoreApiEndpoint):
    config = CoreApiEndpointConfiguration(
        path="/github_installations/query",
        auth_required=False,
        team_id_required=False,
    )

    class RequestBody(BaseRequestBody):
        team: Optional[TeamQueryInput] = None
        github_installation: Optional[GithubInstallationQueryInput] = None

    class ResponseBody(BaseResponseBody):
        team: Optional[Team]
        github_installation: GithubInstallation

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

        body = await cls.make_response(response, cls.ResponseBody)
        return body


class DeleteGithubInstallation(CoreApiEndpoint):
    config = CoreApiEndpointConfiguration(
        path="/github_installations/delete",
        auth_required=False,
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
        **kwargs: Unpack[requests.CommonRequestArgs],
    ) -> ResponseBody:
        response = await requests.make_request(
            config=cls.config,
            input=input,
            team_id=team_id,
            **kwargs,
        )

        body = await cls.make_response(response, cls.ResponseBody)
        return body
