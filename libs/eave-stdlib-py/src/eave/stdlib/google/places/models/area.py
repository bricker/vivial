from typing import TypedDict

from .containment import Containment
from .localized_text import LocalizedText


class Area(TypedDict, total=False):
    name: str
    placeId: str
    displayName: LocalizedText
    containment: Containment
