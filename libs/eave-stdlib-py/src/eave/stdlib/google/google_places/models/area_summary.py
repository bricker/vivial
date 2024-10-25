from dataclasses import dataclass
from .content_block import ContentBlock

@dataclass
class AreaSummary:
    contentBlocks: list[ContentBlock]
