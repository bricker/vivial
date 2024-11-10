from typing import Required, TypedDict


class ListingProperties(TypedDict, total=False):
    """Display/listing details about the event"""

    seatmap_thumbnail_url: str | None
    """URL for the seatmap overview image (only if event is reserved)"""

    is_paid: Required[bool]
    """Does the event have paid tickets?"""
