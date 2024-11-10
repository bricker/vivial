from dataclasses import dataclass
from uuid import UUID


@dataclass(kw_only=True)
class ActivityCategory:
    id: UUID
    name: str


@dataclass(kw_only=True)
class ActivitySubcategory:
    id: UUID
    name: str
    is_default: bool
    is_manually_curated: bool
    category_id: UUID
    eventbrite_subcategory_ids: list[str]


@dataclass(kw_only=True)
class ActivityFormat:
    id: UUID
    name: str
    eventbrite_format_id: str


@dataclass(kw_only=True)
class RestaurantCategory:
    id: UUID
    name: str
    is_default: bool
    google_category_ids: list[str]
