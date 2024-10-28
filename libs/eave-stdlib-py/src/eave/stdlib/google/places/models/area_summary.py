from typing import TypedDict

from .content_block import ContentBlock


class AreaSummary(TypedDict, total=False):
    """https://developers.google.com/maps/documentation/places/web-service/reference/rest/v1/places#AreaSummary"""

    contentBlocks: list[ContentBlock]
