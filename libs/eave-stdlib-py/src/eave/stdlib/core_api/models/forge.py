import enum

from eave.stdlib.core_api.models import BaseInputModel, BaseResponseModel

import pydantic
from typing import Optional



class EaveForgeInboundOperation(enum.StrEnum):
    createDocument = "createDocument"
    updateDocument = "updateDocument"
    archiveDocument = "archiveDocument"


class ForgeInstallation(BaseResponseModel):
    id: pydantic.UUID4
    forge_app_id: str
    forge_app_version: str
    forge_app_installation_id: str
    forge_app_installer_account_id: str
    webtrigger_url: str
    confluence_space_key: Optional[str]


class QueryForgeInstallationInput(BaseInputModel):
    forge_app_id: str
    forge_app_installation_id: str


class RegisterForgeInstallationInput(BaseInputModel):
    """
    These field names MUST match the field names defined in the ORM.
    It is recommended to not change these.
    """

    forge_app_id: str
    forge_app_version: str
    forge_app_installation_id: str
    forge_app_installer_account_id: str
    webtrigger_url: str
    confluence_space_key: Optional[str]


class UpdateForgeInstallationInput(BaseInputModel):
    """
    These field names MUST match the field names defined in the ORM.
    It is recommended to not change these.
    """

    forge_app_installation_id: str
    forge_app_version: Optional[str]
    forge_app_installer_account_id: Optional[str]
    webtrigger_url: Optional[str]
    confluence_space_key: Optional[str]


