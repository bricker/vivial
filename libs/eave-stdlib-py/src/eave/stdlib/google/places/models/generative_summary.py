from typing import TypedDict
from .localized_text import LocalizedText
from .references import References

class GenerativeSummary(TypedDict, total=False):
    overview: LocalizedText
    description: LocalizedText
    references: References
