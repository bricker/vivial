from typing import TypedDict


class ListingProperties(TypedDict, total=False):
    """Display/listing details about the event"""

    seatmap_thumbnail_url: str | None
    """not documented"""

    is_paid: bool | None
    """not documented"""
