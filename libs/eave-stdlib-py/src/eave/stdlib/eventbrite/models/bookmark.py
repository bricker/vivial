from typing import TypedDict


class BookmarkInfo(TypedDict, total=False):
    """The bookmark information on the event, requires the bookmark_info expansion"""

    bookmarked: bool | None
    """User saved the event or not."""
