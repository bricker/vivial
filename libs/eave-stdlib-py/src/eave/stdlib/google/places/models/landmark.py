from typing import TypedDict

from .localized_text import LocalizedText
from .spatial_relationship import SpatialRelationship


class Landmark(TypedDict, total=False):
    """https://developers.google.com/maps/documentation/places/web-service/reference/rest/v1/places#Landmark"""

    name: str
    placeId: str
    displayName: LocalizedText
    types: list[str]
    spatialRelationship: SpatialRelationship
    straightLineDistanceMeters: float
    travelDistanceMeters: float
