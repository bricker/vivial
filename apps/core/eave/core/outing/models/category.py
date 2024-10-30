from dataclasses import dataclass


class Category:
    id: str
    subcategory_id: str | None

    def __init__(self, id: str, subcategory_id: str | None = None) -> None:
        self.id = id
        self.subcategory_id = subcategory_id

@dataclass(kw_only=True)
class ActivityCategory:
    id: str
    name: str

@dataclass(kw_only=True)
class ActivitySubcategory:
    id: str
    name: str
    is_default: bool
    is_manually_curated: bool
    category_id: str
    eventbrite_subcategory_ids: list[str]

@dataclass(kw_only=True)
class RestaurantCategory:
    id: str
    name: str
    is_default: bool
    google_category_ids: list[str]
