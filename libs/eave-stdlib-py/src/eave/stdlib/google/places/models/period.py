from dataclasses import dataclass
from .point import Point

@dataclass
class Period:
    open: Point
    close: Point
