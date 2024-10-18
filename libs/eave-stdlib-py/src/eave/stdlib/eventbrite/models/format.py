from typing import TypedDict


class Format(TypedDict, total=False):
    """https://www.eventbrite.com/platform/api#/reference/formats"""

    id: str | None
    """Format ID"""

    resource_uri: str | None

    name: str | None
    """Format name"""

    name_localized: str | None
    """Localized format name"""

    short_name: str | None
    """Short name for a format"""

    short_name_localized: str | None
    """Localized short name for a format"""
