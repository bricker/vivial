from eave.stdlib.core_api.models.slack import SlackInstallation
from eave.stdlib.core_api.models.slack import SlackInstallationInput
from . import BaseRequestBody, BaseResponseBody, Endpoint, EndpointConfiguration

from eave.stdlib.eave_origins import EaveOrigin
from ..models import team
from ... import requests


class GetSlackInstallation(Endpoint):
    config = EndpointConfiguration(
        path="/integrations/slack/query",
        auth_required=False,
        team_id_required=False,
    )

    class RequestBody(BaseRequestBody):
        slack_integration: SlackInstallationInput

    class ResponseBody(BaseResponseBody):
        team: team.Team
        slack_integration: SlackInstallation

    @classmethod
    async def perform(
        cls,
        origin: EaveOrigin,
        input: RequestBody,
    ) -> ResponseBody:
        response = await requests.make_request(
            url=cls.config.url,
            origin=origin,
            input=input,
        )

        response_json = await response.json()
        return cls.ResponseBody(**response_json, _raw_response=response)
