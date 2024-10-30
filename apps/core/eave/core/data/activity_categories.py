import csv
from dataclasses import dataclass
from uuid import uuid4

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

ACTIVITY_CATEGORIES: list[ActivityCategory] = []

ACTIVITY_SUBCATEGORIES: list[ActivitySubcategory] = []



with open("act_cats.csv", newline="") as f:
    rowiter = csv.DictReader(f)
    for row in rowiter:
        category = next((c for c in ACTIVITY_CATEGORIES if c.name == row["Vivial Category"]), None)

        if category is None:
            category = ActivityCategory(
                id=uuid4().hex,
                name=row["Vivial Category"],
            )
            ACTIVITY_CATEGORIES.append(category)

        subcategory = next((c for c in ACTIVITY_SUBCATEGORIES if c.name == row["Vivial Subcategory"] and c.category_id == category.id), None)

        if subcategory is None:
            subcategory = ActivitySubcategory(
                id=uuid4().hex,
                name=row["Vivial Subcategory"],
                is_default=row["Default?"] == "Yes",
                is_manually_curated=row["In Vivial Curated DB?"] == "TRUE",
                category_id=category.id,
                eventbrite_subcategory_ids=[],
            )
            ACTIVITY_SUBCATEGORIES.append(subcategory)

        ebscid = row["EB Subcategory ID"]
        if ebscid and ebscid not in subcategory.eventbrite_subcategory_ids:
            subcategory.eventbrite_subcategory_ids.append(ebscid)


with open("activity_category_data.py", "w") as f:
    f.write("ACTIVITY_CATEGORIES = [\n")
    for cat in ACTIVITY_CATEGORIES:
        f.writelines([
            "    ActivityCategory(\n",
            f"""        id="{cat.id}",\n""",
            f"""        name="{cat.name}",\n""",
            "    ),\n"
        ])
    f.write("]\n\n")

    f.write("ACTIVITY_SUBCATEGORIES = [\n")
    for subcat in ACTIVITY_SUBCATEGORIES:
        f.writelines([
            "    ActivitySubcategory(\n",
            f"""        id="{subcat.id}",\n""",
            f"""        name="{subcat.name}",\n""",
            f"""        is_default={subcat.is_default},\n""",
            f"""        is_manually_curated={subcat.is_manually_curated},\n""",
            f"""        category_id="{subcat.category_id}",\n""",
            f"""        eventbrite_subcategory_ids={subcat.eventbrite_subcategory_ids},\n""",
            "    ),\n"
        ])
    f.write("]\n")
