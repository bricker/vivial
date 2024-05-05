import uuid
from typing import Unpack

from eave.stdlib.core_api.models.team import Team
from eave.stdlib.endpoints import BaseResponseBody

from ... import requests_util
from . import CoreApiEndpoint, CoreApiEndpointConfiguration


class GetMyTeamRequest(CoreApiEndpoint):
    config = CoreApiEndpointConfiguration(
        path="/_/me/team/query",
        auth_required=True,
        origin_required=True,
        is_public=False,
    )

    class ResponseBody(BaseResponseBody):
        team: Team

    @classmethod
    async def perform(
        cls,
        *,
        account_id: uuid.UUID | None,
        access_token: str | None,
        **kwargs: Unpack[requests_util.CommonRequestArgs],
    ) -> ResponseBody:
        response = await requests_util.make_request(
            config=cls.config,
            input=None,
            account_id=account_id,
            access_token=access_token,
            **kwargs,
        )

        body = await cls.make_response(response, cls.ResponseBody)
        return body
