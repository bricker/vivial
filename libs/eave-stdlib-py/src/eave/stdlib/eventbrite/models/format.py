from typing import TypedDict


class Format(TypedDict, total=False):
    """https://www.eventbrite.com/platform/api#/reference/formats"""

    id: str
    """Format ID"""

    resource_uri: str

    name: str
    """Format name"""

    name_localized: str
    """Localized format name"""

    short_name: str
    """Short name for a format"""

    short_name_localized: str
    """Localized short name for a format"""
