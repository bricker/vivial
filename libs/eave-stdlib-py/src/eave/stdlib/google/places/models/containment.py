from enum import StrEnum


class Containment(StrEnum):
    """https://developers.google.com/maps/documentation/places/web-service/reference/rest/v1/places#Containment"""

    CONTAINMENT_UNSPECIFIED = "CONTAINMENT_UNSPECIFIED"
    WITHIN = "WITHIN"
    OUTSKIRTS = "OUTSKIRTS"
    NEAR = "NEAR"
