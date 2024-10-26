from typing import TypedDict
from .content_block import ContentBlock

class AreaSummary(TypedDict, total=False):
    contentBlocks: list[ContentBlock]
