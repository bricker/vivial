from dataclasses import dataclass
from .date import Date

@dataclass
class Point:
    date: Date
    truncated: bool
    day: int
    hour: int
    minute: int
