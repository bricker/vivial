from typing import Unpack
import uuid
from eave.stdlib.core_api.models.account import AuthenticatedAccount
from eave.stdlib.core_api.models.team import Team
from . import BaseResponseBody, CoreApiEndpoint, CoreApiEndpointConfiguration

from ... import requests


class GetAuthenticatedAccount(CoreApiEndpoint):
    config = CoreApiEndpointConfiguration(
        path="/me/query",
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
        **kwargs: Unpack[requests.CommonRequestArgs],
    ) -> ResponseBody:
        response = await requests.make_request(
            config=cls.config,
            input=None,
            access_token=access_token,
            account_id=account_id,
            team_id=team_id,
            **kwargs,
        )

        body = await cls.make_response(response, cls.ResponseBody)
        return body
