from dataclasses import dataclass

@dataclass
class AccessibilityOptions:
    wheelchairAccessibleParking: bool
    wheelchairAccessibleEntrance: bool
    wheelchairAccessibleRestroom: bool
    wheelchairAccessibleSeating: bool
