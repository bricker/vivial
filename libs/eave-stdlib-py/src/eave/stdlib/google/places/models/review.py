from typing import TypedDict
from .localized_text import LocalizedText
from .author_attribution import AuthorAttribution

class Review(TypedDict, total=False):
    name: str
    relativePublishTimeDescription: str
    text: LocalizedText
    originalText: LocalizedText
    rating: float
    authorAttribution: AuthorAttribution
    publishTime: str
