import uuid
from typing import Unpack

from eave.stdlib.core_api.models.team import Team
from eave.stdlib.endpoints import BaseResponseBody

from ... import requests_util
from . import CoreApiEndpoint, CoreApiEndpointConfiguration


class GetTeamRequest(CoreApiEndpoint):
    config = CoreApiEndpointConfiguration(
        path="/_/team/query",
        signature_required=False,
    )

    class ResponseBody(BaseResponseBody):
        team: Team

    @classmethod
    async def perform(
        cls,
        *,
        team_id: uuid.UUID | str,
        account_id: uuid.UUID | None,
        access_token: str | None,
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
