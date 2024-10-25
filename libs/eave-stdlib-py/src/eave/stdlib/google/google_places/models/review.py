from dataclasses import dataclass
from .localized_text import LocalizedText
from .author_attribution import AuthorAttribution

@dataclass
class Review:
    name: str
    relativePublishTimeDescription: str
    text: LocalizedText
    originalText: LocalizedText
    rating: float
    authorAttribution: AuthorAttribution
    publishTime: str
