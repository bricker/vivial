import uuid
from typing import Unpack

from aiohttp.hdrs import METH_POST

from eave.stdlib.core_api.models.team import Team
from eave.stdlib.endpoints import BaseResponseBody

from ... import requests_util
from . import CoreApiEndpoint, CoreApiEndpointConfiguration


class GetMyTeamRequest(CoreApiEndpoint):
    config = CoreApiEndpointConfiguration(
        path="/public/me/team/query",
        method=METH_POST,
        auth_required=True,
        origin_required=True,
        is_public=True,
    )

    class ResponseBody(BaseResponseBody):
        team: Team

    @classmethod
    async def perform(
        cls,
        *,
        account_id: uuid.UUID | str,
        access_token: str,
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
