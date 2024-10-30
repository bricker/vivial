from typing import TypedDict

from .containment import Containment
from .localized_text import LocalizedText


class Area(TypedDict, total=False):
    """https://developers.google.com/maps/documentation/places/web-service/reference/rest/v1/places#Area"""

    name: str
    placeId: str
    displayName: LocalizedText
    containment: Containment
