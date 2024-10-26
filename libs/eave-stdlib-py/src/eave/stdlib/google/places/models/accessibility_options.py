from typing import TypedDict

class AccessibilityOptions(TypedDict, total=False):
    wheelchairAccessibleParking: bool
    wheelchairAccessibleEntrance: bool
    wheelchairAccessibleRestroom: bool
    wheelchairAccessibleSeating: bool
