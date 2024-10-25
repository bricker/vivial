from dataclasses import dataclass
from .localized_text import LocalizedText
from .containment import Containment

@dataclass
class Area:
    name: str
    placeId: str
    displayName: LocalizedText
    containment: Containment
