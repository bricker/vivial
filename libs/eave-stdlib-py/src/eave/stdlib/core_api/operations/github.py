from typing import Optional
from eave.stdlib.core_api.models.github import GithubInstallation
from eave.stdlib.core_api.models.github import GithubInstallationInput
from eave.stdlib.logging import LogContext
from . import BaseRequestBody, BaseResponseBody, Endpoint, EndpointConfiguration
from eave.stdlib.eave_origins import EaveOrigin

from ..models import team
from ... import requests


class GetGithubInstallation(Endpoint):
    config = EndpointConfiguration(
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
        origin: EaveOrigin,
        input: RequestBody,
        ctx: Optional[LogContext] = None,
    ) -> ResponseBody:
        response = await requests.make_request(
            url=cls.config.url,
            origin=origin,
            input=input,
            ctx=ctx,
        )

        response_json = await response.json()
        return cls.ResponseBody(**response_json, _raw_response=response)
