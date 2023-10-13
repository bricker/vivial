from typing import Optional, Unpack
import uuid
from ... import requests
from eave.stdlib.core_api.models.team import ConfluenceDestination, ConfluenceDestinationInput, Team
from . import BaseRequestBody, BaseResponseBody, CoreApiEndpoint, CoreApiEndpointConfiguration
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
        response = await requests.make_request(
            config=cls.config,
            input=None,
            team_id=team_id,
            account_id=account_id,
            access_token=access_token,
            **kwargs,
        )

        return await cls.make_response(response, cls.ResponseBody)


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
        response = await requests.make_request(
            config=cls.config,
            input=input,
            access_token=access_token,
            account_id=account_id,
            **kwargs,
        )

        response_json = await response.json()
        return cls.ResponseBody(**response_json, _raw_response=response)


# class UpdateTeam(CoreApiEndpoint):
#     config = CoreApiEndpointConfiguration(
#         path="/team/update",
#         auth_required=False,
#     )

#     class RequestBody(BaseRequestBody):
#         team: TeamInput

#     class ResponseBody(BaseResponseBody):
#         team: Team
#         integrations: integrations.Integrations

#     requestBodyType = RequestBody
#     responseBodyType = ResponseBody
