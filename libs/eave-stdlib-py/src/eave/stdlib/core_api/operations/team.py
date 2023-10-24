from typing import Optional, Unpack
import uuid

from eave.stdlib.api_types import BaseRequestBody, BaseResponseBody
from ... import requests
from eave.stdlib.core_api.models.team import ConfluenceDestination, ConfluenceDestinationInput, Team
from . import CoreApiEndpoint, CoreApiEndpointConfiguration
from ..models import integrations


class GetTeamRequest(CoreApiEndpoint):
    config = CoreApiEndpointConfiguration(
        path="/team/query",
        auth_required=False,
    )

    class ResponseBody(BaseResponseBody):
        team: Team
        integrations: integrations.Integrations

    @classmethod
    async def perform(
        cls,
        team_id: uuid.UUID | str,
        account_id: Optional[uuid.UUID],
        access_token: Optional[str],
        **kwargs: Unpack[requests.CommonRequestArgs],
    ) -> ResponseBody:
        return await requests.make_request(
            config=cls.config,
            response_type=cls.ResponseBody,
            input=None,
            team_id=team_id,
            account_id=account_id,
            access_token=access_token,
            **kwargs,
        )


class UpsertConfluenceDestinationAuthedRequest(CoreApiEndpoint):
    config = CoreApiEndpointConfiguration(
        path="/me/team/destinations/confluence/upsert",
        team_id_required=False,
    )

    class RequestBody(BaseRequestBody):
        confluence_destination: ConfluenceDestinationInput

    class ResponseBody(BaseResponseBody):
        team: Team
        confluence_destination: ConfluenceDestination

    @classmethod
    async def perform(
        cls,
        input: RequestBody,
        access_token: str,
        account_id: uuid.UUID | str,
        **kwargs: Unpack[requests.CommonRequestArgs],
    ) -> ResponseBody:
        return await requests.make_request(
            config=cls.config,
            response_type=cls.ResponseBody,
            input=input,
            access_token=access_token,
            account_id=account_id,
            **kwargs,
        )
