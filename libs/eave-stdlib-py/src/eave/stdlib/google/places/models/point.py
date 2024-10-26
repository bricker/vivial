from typing import TypedDict
from .date import Date

class Point(TypedDict, total=False):
    date: Date
    truncated: bool
    day: int
    hour: int
    minute: int
