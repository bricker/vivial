import uuid

from eave.stdlib.core_api.models.team import Team
from . import BaseResponseBody, Endpoint, EndpointConfiguration
from ..models import integrations

from eave.stdlib.eave_origins import EaveOrigin

from ... import requests


class GetTeam(Endpoint):
    config = EndpointConfiguration(
        path="/team/query",
        auth_required=False,
    )

    class ResponseBody(BaseResponseBody):
        team: Team
        integrations: integrations.Integrations

    @classmethod
    async def perform(
        cls,
        origin: EaveOrigin,
        team_id: uuid.UUID,
    ) -> ResponseBody:
        response = await requests.make_request(
            url=cls.config.url,
            origin=origin,
            input=None,
            team_id=team_id,
        )

        response_json = await response.json()
        return cls.ResponseBody(**response_json, _raw_response=response)



