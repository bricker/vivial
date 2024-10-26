from typing import TypedDict
from .localized_text import LocalizedText
from .spatial_relationship import SpatialRelationship

class Landmark(TypedDict, total=False):
    name: str
    placeId: str
    displayName: LocalizedText
    types: list[str]
    spatialRelationship: SpatialRelationship
    straightLineDistanceMeters: float
    travelDistanceMeters: float
