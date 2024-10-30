from enum import StrEnum


class SpatialRelationship(StrEnum):
    """https://developers.google.com/maps/documentation/places/web-service/reference/rest/v1/places#SpatialRelationship"""

    NEAR = "NEAR"
    WITHIN = "WITHIN"
    BESIDE = "BESIDE"
    ACROSS_THE_ROAD = "ACROSS_THE_ROAD"
    DOWN_THE_ROAD = "DOWN_THE_ROAD"
    AROUND_THE_CORNER = "AROUND_THE_CORNER"
    BEHIND = "BEHIND"
