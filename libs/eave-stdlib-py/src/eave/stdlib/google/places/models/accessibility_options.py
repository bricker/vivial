from typing import TypedDict


class AccessibilityOptions(TypedDict, total=False):
    """https://developers.google.com/maps/documentation/places/web-service/reference/rest/v1/places#AccessibilityOptions"""

    wheelchairAccessibleParking: bool
    wheelchairAccessibleEntrance: bool
    wheelchairAccessibleRestroom: bool
    wheelchairAccessibleSeating: bool
