from dataclasses import dataclass
from .localized_text import LocalizedText
from .references import References

@dataclass
class ContentBlock:
    topic: str
    content: LocalizedText
    references: References
