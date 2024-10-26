from typing import TypedDict
from .landmark import Landmark
from .area import Area

class AddressDescriptor(TypedDict, total=False):
    landmarks: list[Landmark]
    areas: list[Area]
