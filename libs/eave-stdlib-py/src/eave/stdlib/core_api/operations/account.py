import uuid
from typing import Unpack

from eave.stdlib.core_api.models.account import AuthenticatedAccount
from eave.stdlib.core_api.models.team import Team
from eave.stdlib.endpoints import BaseResponseBody

from ... import requests_util
from . import CoreApiEndpoint, CoreApiEndpointConfiguration


class GetMyAccountRequest(CoreApiEndpoint):
    config = CoreApiEndpointConfiguration(
        path="/_/me/account/query",
        auth_required=True,
        origin_required=True,
        is_public=False,
    )

    class ResponseBody(BaseResponseBody):
        account: AuthenticatedAccount
        team: Team

    @classmethod
    async def perform(
        cls,
        *,
        access_token: str,
        account_id: uuid.UUID | str,
        **kwargs: Unpack[requests_util.CommonRequestArgs],
    ) -> ResponseBody:
        response = await requests_util.make_request(
            config=cls.config,
            input=None,
            access_token=access_token,
            account_id=account_id,
            **kwargs,
        )

        body = await cls.make_response(response, cls.ResponseBody)
        return body
