from typing import TypedDict

class Date(TypedDict, total=False):
    year: int
    month: int
    day: int
