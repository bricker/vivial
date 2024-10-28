from typing import TypedDict

from .localized_text import LocalizedText
from .references import References


class ContentBlock(TypedDict, total=False):
    topic: str
    content: LocalizedText
    references: References
