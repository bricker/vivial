from typing import TypedDict


class Category(TypedDict, total=False):
    """https://www.eventbrite.com/platform/api#/reference/categories"""

    id: str | None
    """Category ID"""

    resource_uri: str | None

    name: str | None
    """Category name"""

    name_localized: str | None
    """Translated category name"""

    short_name: str | None
    """Shorter category name for display in sidebars and other small spaces"""

    short_name_localized: str | None
    """Translated short category name"""

    subcategories: "list[Subcategory] | None"
    """List of subcategories (only shown on some endpoints)"""


class Subcategory(TypedDict, total=False):
    """https://www.eventbrite.com/platform/api#/reference/categories"""

    id: str | None
    """Subcategory ID"""

    resource_uri: str | None

    name: str | None
    """Subcategory name"""

    name_localized: str | None
    """Translated category name"""

    parent_category: Category | None
    """Category this subcategory belongs to"""
