from typing import Unpack
from eave.stdlib.core_api.models.atlassian import AtlassianInstallation
from eave.stdlib.core_api.models.atlassian import AtlassianInstallationInput
from . import BaseRequestBody, BaseResponseBody, CoreApiEndpoint, CoreApiEndpointConfiguration

from ..models import team
from ... import requests


class GetAtlassianInstallation(CoreApiEndpoint):
    config = CoreApiEndpointConfiguration(
        path="/integrations/atlassian/query",
        auth_required=False,
        team_id_required=False,
    )

    class RequestBody(BaseRequestBody):
        atlassian_integration: AtlassianInstallationInput

    class ResponseBody(BaseResponseBody):
        team: team.Team
        atlassian_integration: AtlassianInstallation

    @classmethod
    async def perform(
        cls,
        input: RequestBody,
        **kwargs: Unpack[requests.CommonRequestArgs],
    ) -> ResponseBody:
        response = await requests.make_request(config=cls.config, input=input, **kwargs)
        body = await cls.make_response(response, cls.ResponseBody)
        return body