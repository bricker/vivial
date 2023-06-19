from typing import Optional
import uuid
from eave.stdlib.core_api.models.account import AuthenticatedAccount
from eave.stdlib.core_api.models.team import Destination, Team
from eave.stdlib.logging import LogContext
from . import BaseResponseBody, EndpointConfiguration

from eave.stdlib.eave_origins import EaveOrigin
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
        cls,
        origin: EaveOrigin,
        access_token: str,
        account_id: uuid.UUID,
        ctx: Optional[LogContext] = None,
    ) -> ResponseBody:
        response = await requests.make_request(
            url=cls.config.url,
            origin=origin,
            input=None,
            access_token=access_token,
            account_id=account_id,
            ctx=ctx,
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
        destination: Destination | None

    @classmethod
    async def perform(
        cls,
        origin: EaveOrigin,
        access_token: str,
        account_id: uuid.UUID,
        ctx: Optional[LogContext] = None,
    ) -> ResponseBody:
        response = await requests.make_request(
            url=cls.config.url,
            origin=origin,
            input=None,
            access_token=access_token,
            account_id=account_id,
            ctx=ctx,
        )

        response_json = await response.json()
        return cls.ResponseBody(**response_json, _raw_response=response)
