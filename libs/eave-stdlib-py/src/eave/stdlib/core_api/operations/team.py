from typing import Optional, Unpack
import uuid
from ... import requests_util
from eave.stdlib.core_api.models.team import Team
from . import BaseResponseBody, CoreApiEndpoint, CoreApiEndpointConfiguration


class GetTeamRequest(CoreApiEndpoint):
    config = CoreApiEndpointConfiguration(
        path="/team/query",
        auth_required=False,
    )

    class ResponseBody(BaseResponseBody):
        team: Team

    @classmethod
    async def perform(
        cls,
        team_id: uuid.UUID | str,
        account_id: Optional[uuid.UUID],
        access_token: Optional[str],
        **kwargs: Unpack[requests_util.CommonRequestArgs],
    ) -> ResponseBody:
        response = await requests_util.make_request(
            config=cls.config,
            input=None,
            team_id=team_id,
            account_id=account_id,
            access_token=access_token,
            **kwargs,
        )

        body = await cls.make_response(response, cls.ResponseBody)
        return body
