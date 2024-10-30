from dataclasses import dataclass
import json
import csv
from uuid import UUID, uuid4

@dataclass(kw_only=True)
class ActivityCategory:
    id: str
    name: str
    eventbrite_category_id: str | None

@dataclass(kw_only=True)
class ActivitySubcategory:
    id: str
    name: str
    is_default: bool
    is_manually_curated: bool
    category_id: str
    eventbrite_subcategory_id: str | None

CATEGORIES: list[ActivityCategory] = []
SUBCATEGORIES: list[ActivitySubcategory] = []

with open("activity_categories.csv", newline="") as f:
    rowiter = csv.DictReader(f)
    for row in rowiter:
        category = next((c for c in CATEGORIES if c.name == row["Vivial Category"]), None)

        if category is None:
            category = ActivityCategory(
                id=uuid4().hex,
                name=row["Vivial Category"],
                eventbrite_category_id=row["EB Category ID"],
            )
            CATEGORIES.append(category)

        SUBCATEGORIES.append(
            ActivitySubcategory(
                id=uuid4().hex,
                name=row["Vivial Subcategory"],
                is_default=row["Default?"] == "Yes",
                is_manually_curated=row["In Vivial Curated DB?"] == "TRUE",
                category_id=category.id,
                eventbrite_subcategory_id=row["EB Subcategory ID"],
            )
        )

with open("activity_categories.json", "w") as f:
    json.dump([c.__dict__ for c in CATEGORIES], f, indent=2, sort_keys=True)

with open("activity_subcategories.json", "w") as f:
    json.dump([c.__dict__ for c in SUBCATEGORIES], f, indent=2, sort_keys=True)
