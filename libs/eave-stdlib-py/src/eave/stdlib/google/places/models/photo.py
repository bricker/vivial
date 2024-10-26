from typing import TypedDict
from .author_attribution import AuthorAttribution

class Photo(TypedDict, total=False):
    name: str
    widthPx: int
    heightPx: int
    authorAttributions: list[AuthorAttribution]
