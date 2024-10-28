from typing import TypedDict

from .area import Area
from .landmark import Landmark


class AddressDescriptor(TypedDict, total=False):
    """https://developers.google.com/maps/documentation/places/web-service/reference/rest/v1/places#AddressDescriptor"""

    landmarks: list[Landmark]
    areas: list[Area]
