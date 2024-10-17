from typing import TypedDict


class Pagination(TypedDict, total=False):
    """https://www.eventbrite.com/platform/api#/introduction/paginated-responses"""

    object_count: int | None
    """The total number of objects across all pages (optional)"""

    page_number: int | None
    """The current page number (starts at 1)"""

    page_size: int | None
    """The number of objects on each page (roughly)"""

    page_count: int | None
    """The total number of pages (starting at 1) (optional)"""

    continuation: str | None
    """A token to return to the server to get the next set of results"""

    has_more_items: bool | None
    """nodoc"""
