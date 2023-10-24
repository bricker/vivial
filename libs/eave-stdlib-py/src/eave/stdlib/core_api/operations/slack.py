from typing import Unpack
from eave.stdlib.api_types import BaseRequestBody, BaseResponseBody
from eave.stdlib.core_api.models.slack import SlackInstallation
from eave.stdlib.core_api.models.slack import SlackInstallationInput
from . import CoreApiEndpoint, CoreApiEndpointConfiguration

from ..models import team
from ... import requests


class GetSlackInstallation(CoreApiEndpoint):
    config = CoreApiEndpointConfiguration(
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
        input: RequestBody,
        **kwargs: Unpack[requests.CommonRequestArgs],
    ) -> ResponseBody:
        return await requests.make_request(
            config=cls.config,
            response_type=cls.ResponseBody,
            input=input,
            **kwargs,
        )
