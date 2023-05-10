import typing

import pydantic
from .base import EndpointConfiguration, Endpoint
from .. import models

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
    confluence_space_key: typing.Optional[str]

class UpdateForgeInstallationInput(pydantic.BaseModel):
    """
    These field names MUST match the field names defined in the ORM.
    It is recommended to not change these.
    """
    forge_app_installation_id: str
    forge_app_version: typing.Optional[str]
    forge_app_installer_account_id: typing.Optional[str]
    confluence_space_key: typing.Optional[str]

class ForgeWebTriggerInput(pydantic.BaseModel):
    """
    These field names MUST match the field names defined in the ORM.
    It is recommended to not change these.
    """
    webtrigger_key: str
    webtrigger_url: str

class QueryForgeInstallation(Endpoint):
    config = EndpointConfiguration(
        path = "/integrations/forge/query",
        auth_required = False,
        team_id_required = False,
        signature_required = False,
        origin_required = False,
    )
    class RequestBody(pydantic.BaseModel):
        forge_integration: QueryForgeInstallationInput

    class ResponseBody(pydantic.BaseModel):
        team: models.Team
        forge_integration: models.forge.ForgeInstallation
        forge_web_triggers: typing.Mapping[str, models.forge.ForgeWebTrigger]

class RegisterForgeInstallation(Endpoint):
    config = EndpointConfiguration(
        path = "/integrations/forge/register",
        auth_required = False,
        team_id_required = False,
        signature_required = False,
        origin_required = False,
    )

    class RequestBody(pydantic.BaseModel):
        forge_integration: RegisterForgeInstallationInput
        forge_web_triggers: typing.Optional[typing.Mapping[str, ForgeWebTriggerInput]]

    class ResponseBody(pydantic.BaseModel):
        team: models.Team
        forge_integration: models.forge.ForgeInstallation
        forge_web_triggers: typing.Mapping[str, models.forge.ForgeWebTrigger]

class UpdateForgeInstallation(Endpoint):
    config = EndpointConfiguration(
        path = "/integrations/forge/update",
        auth_required = False,
        team_id_required = False,
        signature_required = False,
        origin_required = False,
    )

    class RequestBody(pydantic.BaseModel):
        forge_integration: UpdateForgeInstallationInput
        forge_web_triggers: typing.Optional[typing.Mapping[str, ForgeWebTriggerInput]]

    class ResponseBody(pydantic.BaseModel):
        team: models.Team
        forge_integration: models.forge.ForgeInstallation
        forge_web_triggers: typing.Mapping[str, models.forge.ForgeWebTrigger]