import enum

from eave.stdlib.core_api.models import BaseInputModel, BaseResponseModel

import pydantic
from typing import Optional

class ConfluenceDestination(BaseResponseModel):
    space_key: Optional[str]

class ConfluenceDestinationInput(BaseInputModel):
    space_key: str

class TeamInput(BaseInputModel):
    name: Optional[str]
    document_platform: Optional[str]
    beta_whitelisted: Optional[bool]


class DocumentPlatform(enum.StrEnum):
    eave = "eave"
    confluence = "confluence"
    google_drive = "google_drive"


class Team(BaseResponseModel):
    id: pydantic.UUID4
    name: str
    document_platform: Optional[DocumentPlatform]
    beta_whitelisted: bool = False
