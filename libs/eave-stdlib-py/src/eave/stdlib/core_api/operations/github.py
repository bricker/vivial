from typing import Unpack
import uuid
from eave.stdlib.api_types import BaseRequestBody, BaseResponseBody
from eave.stdlib.core_api.models.github import GithubInstallation
from eave.stdlib.core_api.models.github import GithubInstallationInput
from . import CoreApiEndpoint, CoreApiEndpointConfiguration

from ..models import team
from ... import requests


class GetGithubInstallation(CoreApiEndpoint):
    config = CoreApiEndpointConfiguration(
        path="/integrations/github/query",
        auth_required=False,
        team_id_required=False,
    )

    class RequestBody(BaseRequestBody):
        github_integration: GithubInstallationInput

    class ResponseBody(BaseResponseBody):
        team: team.Team
        github_integration: GithubInstallation

    @classmethod
    async def perform(
        cls,
        input: RequestBody,
        **kwargs: Unpack[requests.CommonRequestArgs],
    ) -> ResponseBody:
        return await requests.make_request(
            config=cls.config,
            response_type=cls.ResponseBody,
            input=input,
            **kwargs,
        )


class DeleteGithubInstallation(CoreApiEndpoint):
    config = CoreApiEndpointConfiguration(
        path="/integrations/github/delete",
        auth_required=False,
    )

    class RequestBody(BaseRequestBody):
        github_integration: GithubInstallationInput

    class ResponseBody(BaseResponseBody):
        pass

    @classmethod
    async def perform(
        cls,
        input: RequestBody,
        team_id: uuid.UUID,
        **kwargs: Unpack[requests.CommonRequestArgs],
    ) -> ResponseBody:
        return await requests.make_request(
            config=cls.config,
            response_type=cls.ResponseBody,
            input=input,
            team_id=team_id,
            **kwargs,
        )
