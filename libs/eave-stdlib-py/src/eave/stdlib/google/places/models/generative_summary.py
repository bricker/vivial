from dataclasses import dataclass
from .localized_text import LocalizedText
from .references import References

@dataclass
class GenerativeSummary:
    overview: LocalizedText
    description: LocalizedText
    references: References
