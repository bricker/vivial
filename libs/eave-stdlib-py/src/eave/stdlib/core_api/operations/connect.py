from typing import Optional, Unpack
from eave.stdlib.api_types import BaseRequestBody, BaseResponseBody
from eave.stdlib.core_api.models import team
from eave.stdlib.core_api.models.connect import (
    ConnectInstallation,
    QueryConnectInstallationInput,
    RegisterConnectInstallationInput,
)

from . import CoreApiEndpoint, CoreApiEndpointConfiguration


from ... import requests


class RegisterConnectIntegrationRequest(CoreApiEndpoint):
    config = CoreApiEndpointConfiguration(
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
        return await requests.make_request(
            config=cls.config,
            response_type=cls.ResponseBody,
            input=input,
            **kwargs,
        )


class QueryConnectIntegrationRequest(CoreApiEndpoint):
    config = CoreApiEndpointConfiguration(
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
        return await requests.make_request(
            config=cls.config,
            response_type=cls.ResponseBody,
            input=input,
            **kwargs,
        )
