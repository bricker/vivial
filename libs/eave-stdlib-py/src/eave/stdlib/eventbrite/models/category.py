from typing import Required, TypedDict


class Category(TypedDict, total=False):
    """https://www.eventbrite.com/platform/api#/reference/categories"""

    id: Required[str]
    """Category ID"""

    resource_uri: Required[str]

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

    id: Required[str]
    """Subcategory ID"""

    resource_uri: Required[str]

    name: str | None
    """Subcategory name"""

    name_localized: str | None
    """Translated category name"""

    parent_category: Category | None
    """Category this subcategory belongs to"""
