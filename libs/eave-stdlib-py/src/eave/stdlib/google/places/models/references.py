from typing import TypedDict

from .review import Review


class References(TypedDict, total=False):
    reviews: list[Review]
    places: list[str]
