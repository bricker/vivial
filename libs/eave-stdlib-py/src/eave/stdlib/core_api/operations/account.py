import uuid
from typing import Unpack

from eave.stdlib.core_api.models.account import AuthenticatedAccount
from eave.stdlib.core_api.models.team import Team
from eave.stdlib.endpoints import BaseResponseBody

from ... import requests_util
from . import CoreApiEndpoint, CoreApiEndpointConfiguration


class GetAuthenticatedAccount(CoreApiEndpoint):
    config = CoreApiEndpointConfiguration(
        path="/_/me/query",
        signature_required=False,
    )

    class ResponseBody(BaseResponseBody):
        account: AuthenticatedAccount
        team: Team

    @classmethod
    async def perform(
        cls,
        access_token: str,
        team_id: uuid.UUID | str,
        account_id: uuid.UUID | str,
        **kwargs: Unpack[requests_util.CommonRequestArgs],
    ) -> ResponseBody:
        response = await requests_util.make_request(
            config=cls.config,
            input=None,
            access_token=access_token,
            account_id=account_id,
            team_id=team_id,
            **kwargs,
        )

        body = await cls.make_response(response, cls.ResponseBody)
        return body
