from typing import Optional, Unpack
from eave.stdlib.core_api.models import team
from eave.stdlib.core_api.models.connect import (
    ConnectInstallation,
    QueryConnectInstallationInput,
    RegisterConnectInstallationInput,
)

from . import BaseRequestBody, BaseResponseBody, Endpoint, EndpointConfiguration


from ... import requests


class RegisterConnectIntegrationRequest(Endpoint):
    config = EndpointConfiguration(
        path="/integrations/connect/register",
        auth_required=False,
        team_id_required=False,
        signature_required=True,
        origin_required=True,
    )

    class RequestBody(BaseRequestBody):
        connect_integration: RegisterConnectInstallationInput

    class ResponseBody(BaseResponseBody):
        team: Optional[team.Team]
        connect_integration: ConnectInstallation

    @classmethod
    async def perform(
        cls,
        input: RequestBody,
        **kwargs: Unpack[requests.CommonRequestArgs],
    ) -> ResponseBody:
        response = await requests.make_request(
            url=cls.config.url,
            input=input,
            **kwargs,
        )

        response_json = await response.json()
        return cls.ResponseBody(**response_json, _raw_response=response)


class QueryConnectIntegrationRequest(Endpoint):
    config = EndpointConfiguration(
        path="/integrations/connect/query",
        auth_required=False,
        team_id_required=False,
        signature_required=True,
        origin_required=True,
    )

    class RequestBody(BaseRequestBody):
        connect_integration: QueryConnectInstallationInput

    class ResponseBody(BaseResponseBody):
        team: Optional[team.Team]
        connect_integration: ConnectInstallation

    @classmethod
    async def perform(
        cls,
        input: RequestBody,
        **kwargs: Unpack[requests.CommonRequestArgs],
    ) -> ResponseBody:
        response = await requests.make_request(
            url=cls.config.url,
            input=input,
            **kwargs,
        )

        response_json = await response.json()
        return cls.ResponseBody(**response_json, _raw_response=response)
