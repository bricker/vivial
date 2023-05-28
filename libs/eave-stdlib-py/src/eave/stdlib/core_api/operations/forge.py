import typing
import uuid

import pydantic

from eave.stdlib.requests import make_request
from .base import EndpointConfiguration, Endpoint
from ..models.base import EaveBaseModel
from ..models import Team


class ForgeInstallation(EaveBaseModel):
    id: pydantic.UUID4
    forge_app_id: str
    forge_app_version: str
    forge_app_installation_id: str
    forge_app_installer_account_id: str
    webtrigger_url: str
    confluence_space_key: typing.Optional[str]

    class Config:
        orm_mode = True


class QueryForgeInstallationInput(pydantic.BaseModel):
    forge_app_id: str
    forge_app_installation_id: str


class RegisterForgeInstallationInput(pydantic.BaseModel):
    """
    These field names MUST match the field names defined in the ORM.
    It is recommended to not change these.
    """

    forge_app_id: str
    forge_app_version: str
    forge_app_installation_id: str
    forge_app_installer_account_id: str
    webtrigger_url: str
    confluence_space_key: typing.Optional[str]


class UpdateForgeInstallationInput(pydantic.BaseModel):
    """
    These field names MUST match the field names defined in the ORM.
    It is recommended to not change these.
    """

    forge_app_installation_id: str
    forge_app_version: typing.Optional[str]
    forge_app_installer_account_id: typing.Optional[str]
    webtrigger_url: str
    confluence_space_key: typing.Optional[str]


class QueryForgeInstallation(Endpoint):
    config = EndpointConfiguration(
        path="/integrations/forge/query",
        auth_required=False,
        team_id_required=False,
        signature_required=True,
        origin_required=True,
    )

    class RequestBody(pydantic.BaseModel):
        forge_integration: QueryForgeInstallationInput

    class ResponseBody(pydantic.BaseModel):
        team: typing.Optional[Team]
        forge_integration: ForgeInstallation


class RegisterForgeInstallation(Endpoint):
    config = EndpointConfiguration(
        path="/integrations/forge/register",
        auth_required=False,
        team_id_required=False,
        signature_required=True,
        origin_required=True,
    )

    class RequestBody(pydantic.BaseModel):
        forge_integration: RegisterForgeInstallationInput

    class ResponseBody(pydantic.BaseModel):
        forge_integration: ForgeInstallation


class UpdateForgeInstallation(Endpoint):
    config = EndpointConfiguration(
        path="/integrations/forge/update",
        auth_required=False,
        team_id_required=False,
        signature_required=True,
        origin_required=True,
    )

    class RequestBody(pydantic.BaseModel):
        forge_integration: UpdateForgeInstallationInput

    class ResponseBody(pydantic.BaseModel):
        team: typing.Optional[Team]
        forge_integration: ForgeInstallation


async def query_forge_installation(
    input: QueryForgeInstallation.RequestBody,
) -> QueryForgeInstallation.ResponseBody:
    response = await make_request(
        url=QueryForgeInstallation.config.url,
        input=input,
    )

    response_json = await response.json()
    return QueryForgeInstallation.ResponseBody(**response_json)


async def register_forge_installation(
    input: RegisterForgeInstallation.RequestBody,
) -> RegisterForgeInstallation.ResponseBody:
    response = await make_request(
        url=RegisterForgeInstallation.config.url,
        input=input,
    )

    response_json = await response.json()
    return RegisterForgeInstallation.ResponseBody(**response_json)


async def update_forge_installation_authed(
    account_id: uuid.UUID,
    access_token: str,
    input: UpdateForgeInstallation.RequestBody,
) -> UpdateForgeInstallation.ResponseBody:
    response = await make_request(
        url=UpdateForgeInstallation.config.url,
        input=input,
        access_token=access_token,
        account_id=account_id,
    )

    response_json = await response.json()
    return UpdateForgeInstallation.ResponseBody(**response_json)
