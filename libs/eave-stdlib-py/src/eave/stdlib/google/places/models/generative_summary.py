from typing import TypedDict

from .localized_text import LocalizedText
from .references import References


class GenerativeSummary(TypedDict, total=False):
    """https://developers.google.com/maps/documentation/places/web-service/reference/rest/v1/places#GenerativeSummary"""

    overview: LocalizedText
    description: LocalizedText
    references: References
