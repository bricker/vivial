import uuid
from eave.stdlib import requests
from eave.stdlib.core_api.models.team import ConfluenceDestination, ConfluenceDestinationInput, Team, TeamInput
from eave.stdlib.eave_origins import EaveOrigin
from . import BaseRequestBody, BaseResponseBody, Endpoint, EndpointConfiguration
from ..models import integrations


class GetTeam(Endpoint):
    config = EndpointConfiguration(
        path="/team/query",
        auth_required=False,
    )

    class ResponseBody(BaseResponseBody):
        team: Team
        integrations: integrations.Integrations

    @classmethod
    async def perform(
        cls,
        origin: EaveOrigin,
        team_id: uuid.UUID,
    ) -> ResponseBody:
        response = await requests.make_request(
            url=cls.config.url,
            origin=origin,
            input=None,
            team_id=team_id,
        )

        response_json = await response.json()
        return cls.ResponseBody(**response_json, _raw_response=response)

class UpdateConfluenceDestinationAuthed(Endpoint):
    config = EndpointConfiguration(
        path="/me/team/destinations/confluence/update",
    )

    class RequestBody(BaseRequestBody):
        confluence_destination: ConfluenceDestinationInput

    class ResponseBody(BaseResponseBody):
        confluence_destination: ConfluenceDestination

    @classmethod
    async def perform(
        cls,
        origin: EaveOrigin,
        input: RequestBody,
        access_token:  str,
        account_id: uuid.UUID,
    ) -> ResponseBody:
        response = await requests.make_request(
            url=cls.config.url,
            origin=origin,
            input=input,
            access_token=access_token,
            account_id=account_id,
        )

        response_json = await response.json()
        return cls.ResponseBody(**response_json, _raw_response=response)

class CreateConfluenceDestinationAuthed(Endpoint):
    config = EndpointConfiguration(
        path="/me/team/destinations/confluence/create",
    )

    class RequestBody(BaseRequestBody):
        confluence_destination: ConfluenceDestinationInput

    class ResponseBody(BaseResponseBody):
        confluence_destination: ConfluenceDestination

    @classmethod
    async def perform(
        cls,
        origin: EaveOrigin,
        input: RequestBody,
        access_token:  str,
        account_id: uuid.UUID,
    ) -> ResponseBody:
        response = await requests.make_request(
            url=cls.config.url,
            origin=origin,
            input=input,
            access_token=access_token,
            account_id=account_id,
        )

        response_json = await response.json()
        return cls.ResponseBody(**response_json, _raw_response=response)

# class UpdateTeam(Endpoint):
#     config = EndpointConfiguration(
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
