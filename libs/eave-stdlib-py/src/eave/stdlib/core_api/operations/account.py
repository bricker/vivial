from typing import Optional, Unpack
import uuid
from eave.stdlib.core_api.models.account import AuthenticatedAccount
from eave.stdlib.core_api.models.team import Destination, Team
from . import BaseResponseBody, EndpointConfiguration

from . import Endpoint
from ..models.integrations import Integrations
from ... import requests


class GetAuthenticatedAccount(Endpoint):
    config = EndpointConfiguration(
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
            url=cls.config.url,
            input=None,
            access_token=access_token,
            account_id=account_id,
            **kwargs,
        )

        response_json = await response.json()
        return cls.ResponseBody(**response_json, _raw_response=response)


class GetAuthenticatedAccountTeamIntegrations(Endpoint):
    config = EndpointConfiguration(
        path="/me/team/integrations/query",
        team_id_required=False,
    )

    class ResponseBody(BaseResponseBody):
        account: AuthenticatedAccount
        team: Team
        integrations: Integrations
        destination: Optional[Destination]

    @classmethod
    async def perform(
        cls,
        access_token: str,
        account_id: uuid.UUID | str,
        **kwargs: Unpack[requests.CommonRequestArgs],
    ) -> ResponseBody:
        response = await requests.make_request(
            url=cls.config.url,
            input=None,
            access_token=access_token,
            account_id=account_id,
            **kwargs,
        )

        response_json = await response.json()
        return cls.ResponseBody(**response_json, _raw_response=response)
