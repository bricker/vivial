from typing import TypedDict

from .date import Date


class SpecialDay(TypedDict, total=False):
    date: Date
