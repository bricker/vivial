from typing import TypedDict

from .area import Area
from .landmark import Landmark


class AddressDescriptor(TypedDict, total=False):
    landmarks: list[Landmark]
    areas: list[Area]
