from dataclasses import dataclass
from .author_attribution import AuthorAttribution

@dataclass
class Photo:
    name: str
    widthPx: int
    heightPx: int
    authorAttributions: list[AuthorAttribution]
