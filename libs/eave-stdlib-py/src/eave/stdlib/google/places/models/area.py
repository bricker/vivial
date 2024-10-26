from typing import TypedDict
from .localized_text import LocalizedText
from .containment import Containment

class Area(TypedDict, total=False):
    name: str
    placeId: str
    displayName: LocalizedText
    containment: Containment
