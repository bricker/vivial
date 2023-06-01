from typing import Optional
import uuid
from eave.stdlib.core_api.models import team

from eave.stdlib.core_api.models.forge import ForgeInstallation, QueryForgeInstallationInput
from eave.stdlib.core_api.models.forge import RegisterForgeInstallationInput
from eave.stdlib.core_api.models.forge import UpdateForgeInstallationInput
from eave.stdlib.core_api.operations import BaseRequestBody, BaseResponseBody, Endpoint, EndpointConfiguration
from . import BaseRequestBody, BaseResponseBody, Endpoint, EndpointConfiguration

from eave.stdlib.eave_origins import EaveOrigin

from ..models import team
from ... import requests


class RegisterForgeInstallation(Endpoint):
    config = EndpointConfiguration(
        path="/integrations/forge/register",
        auth_required=False,
        team_id_required=False,
        signature_required=False,  # FIXME: Get signing working from Forge
        origin_required=True,
    )

    class RequestBody(BaseRequestBody):
        forge_integration: RegisterForgeInstallationInput

    class ResponseBody(BaseResponseBody):
        forge_integration: ForgeInstallation

    @classmethod
    async def perform(cls,
        origin: EaveOrigin,
        input: RequestBody,
    ) -> ResponseBody:
        response = await requests.make_request(
            url=cls.config.url,
            origin=origin,
            input=input,
        )

        response_json = await response.json()
        return cls.ResponseBody(**response_json)


class UpdateForgeInstallation(Endpoint):
    config = EndpointConfiguration(
        path="/integrations/forge/update",
        auth_required=False,
        team_id_required=False,
        signature_required=True,
        origin_required=True,
    )

    class RequestBody(BaseRequestBody):
        forge_integration: UpdateForgeInstallationInput

    class ResponseBody(BaseResponseBody):
        team: Optional[team.Team]
        forge_integration: ForgeInstallation


    @classmethod
    async def perform(cls,
        origin: EaveOrigin,
        input: RequestBody,
    ) -> ResponseBody:
        response = await requests.make_request(
            url=cls.config.url,
            origin=origin,
            input=input,
        )

        response_json = await response.json()
        return cls.ResponseBody(**response_json)


    @classmethod
    async def perform_authed(cls,
        origin: EaveOrigin,
        account_id: uuid.UUID,
        access_token: str,
        input: RequestBody,
    ) -> ResponseBody:
        response = await requests.make_request(
            url=cls.config.url,
            origin=origin,
            input=input,
            access_token=access_token,
            account_id=account_id,
        )

        response_json = await response.json()
        return cls.ResponseBody(**response_json)






class QueryForgeInstallation(Endpoint):
    config = EndpointConfiguration(
        path="/integrations/forge/query",
        auth_required=False,
        team_id_required=False,
        signature_required=True,
        origin_required=True,
    )

    class RequestBody(BaseRequestBody):
        forge_integration: QueryForgeInstallationInput

    class ResponseBody(BaseResponseBody):
        team: Optional[team.Team]
        forge_integration: ForgeInstallation

    @classmethod
    async def perform(cls,
        origin: EaveOrigin,
        input: RequestBody,
    ) -> ResponseBody:
        response = await requests.make_request(
            url=cls.config.url,
            origin=origin,
            input=input,
        )

        response_json = await response.json()
        return cls.ResponseBody(**response_json)
