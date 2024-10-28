from typing import TypedDict

from .author_attribution import AuthorAttribution
from .localized_text import LocalizedText


class Review(TypedDict, total=False):
    name: str
    relativePublishTimeDescription: str
    text: LocalizedText
    originalText: LocalizedText
    rating: float
    authorAttribution: AuthorAttribution
    publishTime: str
