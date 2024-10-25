from dataclasses import dataclass
from .localized_text import LocalizedText
from .spatial_relationship import SpatialRelationship

@dataclass
class Landmark:
    name: str
    placeId: str
    displayName: LocalizedText
    types: list[str]
    spatialRelationship: SpatialRelationship
    straightLineDistanceMeters: float
    travelDistanceMeters: float
