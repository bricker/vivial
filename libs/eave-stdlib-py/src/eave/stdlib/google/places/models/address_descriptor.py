from dataclasses import dataclass
from .landmark import Landmark
from .area import Area

@dataclass
class AddressDescriptor:
    landmarks: list[Landmark]
    areas: list[Area]
