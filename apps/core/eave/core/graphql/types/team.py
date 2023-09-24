import strawberry
import enum
import uuid

from eave.stdlib.core_api.models import BaseInputModel, BaseResponseModel

from typing import Optional

@strawberry.enum
class DocumentPlatform(enum.StrEnum):
    eave = "eave"
    confluence = "confluence"
    google_drive = "google_drive"

@strawberry.type
class ConfluenceDestination:
    id: uuid.UUID
    space_key: Optional[str]

@strawberry.type
class Destination:
    confluence_destination: Optional[ConfluenceDestination]

@strawberry.type
class AnalyticsTeam:
    id: uuid.UUID
    name: str
    document_platform: Optional[DocumentPlatform]

@strawberry.type
class Team:
    id: uuid.UUID
    name: str
    document_platform: Optional[DocumentPlatform]

@strawberry.input
class ConfluenceDestinationInput:
    space_key: str

@strawberry.input
class TeamInput:
    name: Optional[str]
    document_platform: Optional[str]
