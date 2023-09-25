from typing import Unpack
import uuid
from eave.stdlib.core_api.models.account import AuthenticatedAccount
from eave.stdlib.core_api.models.team import Destination, Team
from . import BaseResponseBody, CoreApiEndpoint, CoreApiEndpointConfiguration

from ..models.integrations import Integrations
from ... import requests


class GetAuthenticatedAccount(CoreApiEndpoint):
    config = CoreApiEndpointConfiguration(
        path="/me/query",
        team_id_required=False,
    )

    class ResponseBody(BaseResponseBody):
        account: AuthenticatedAccount
        team: Team

    @classmethod
    async def perform(
        cls, access_token: str, account_id: uuid.UUID | str, **kwargs: Unpack[requests.CommonRequestArgs]
    ) -> ResponseBody:
        response = await requests.make_request(
            config=cls.config,
            input=None,
            access_token=access_token,
            account_id=account_id,
            **kwargs,
        )

        response_json = await response.json()
        return cls.ResponseBody(**response_json, _raw_response=response)


class GetAuthenticatedAccountTeamIntegrations(CoreApiEndpoint):
    config = CoreApiEndpointConfiguration(
        path="/me/team/integrations/query",
        team_id_required=False,
    )

    class ResponseBody(BaseResponseBody):
        account: AuthenticatedAccount
        team: Team
        integrations: Integrations
        destination: Destination | None

    @classmethod
    async def perform(
        cls,
        access_token: str,
        account_id: uuid.UUID | str,
        **kwargs: Unpack[requests.CommonRequestArgs],
    ) -> ResponseBody:
        response = await requests.make_request(
            config=cls.config,
            input=None,
            access_token=access_token,
            account_id=account_id,
            **kwargs,
        )

        response_json = await response.json()
        return cls.ResponseBody(**response_json, _raw_response=response)
