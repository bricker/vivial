from typing import Unpack
from eave.stdlib.core_api.models.atlassian import AtlassianInstallation
from eave.stdlib.core_api.models.atlassian import AtlassianInstallationInput
from . import BaseRequestBody, BaseResponseBody, Endpoint, EndpointConfiguration

from ..models import team
from ... import requests


class GetAtlassianInstallation(Endpoint):
    config = EndpointConfiguration(
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
        response = await requests.make_request(url=cls.config.url, input=input, **kwargs)

        response_json = await response.json()
        return cls.ResponseBody(**response_json, _raw_response=response)
