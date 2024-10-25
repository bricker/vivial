from dataclasses import dataclass
from .review import Review

@dataclass
class References:
    reviews: list[Review]
    places: list[str]
