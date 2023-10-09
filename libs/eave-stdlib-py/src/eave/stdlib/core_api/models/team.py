import enum
import uuid

from eave.stdlib.core_api.models import BaseInputModel, BaseResponseModel

from typing import Optional


class ConfluenceDestination(BaseResponseModel):
    id: uuid.UUID
    space_key: Optional[str]


class Destination(BaseResponseModel):
    confluence_destination: Optional[ConfluenceDestination]


class ConfluenceDestinationInput(BaseInputModel):
    space_key: str


class TeamInput(BaseInputModel):
    name: Optional[str]
    document_platform: Optional[str]


class DocumentPlatform(enum.StrEnum):
    eave = "eave"
    confluence = "confluence"
    google_drive = "google_drive"


class AnalyticsTeam(BaseResponseModel):
    id: uuid.UUID
    name: str
    document_platform: Optional[DocumentPlatform]


class Team(BaseResponseModel):
    id: uuid.UUID
    name: str
    document_platform: Optional[DocumentPlatform]
    beta_whitelisted: bool = False  # DEPRECATED
