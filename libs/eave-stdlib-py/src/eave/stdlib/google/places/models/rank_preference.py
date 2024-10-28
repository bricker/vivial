from enum import StrEnum


class RankPreference(StrEnum):
    """https://developers.google.com/maps/documentation/places/web-service/nearby-search"""

    POPULARITY = "POPULARITY"
    DISTANCE = "DISTANCE"
