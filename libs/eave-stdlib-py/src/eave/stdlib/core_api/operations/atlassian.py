from typing import Unpack
from eave.stdlib.api_types import BaseRequestBody, BaseResponseBody
from eave.stdlib.core_api.models.atlassian import AtlassianInstallation
from eave.stdlib.core_api.models.atlassian import AtlassianInstallationInput
from . import CoreApiEndpoint, CoreApiEndpointConfiguration

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
        return await requests.make_request(config=cls.config, response_type=cls.ResponseBody, input=input, **kwargs)
