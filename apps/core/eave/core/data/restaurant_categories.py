import csv
from dataclasses import dataclass
from uuid import uuid4

@dataclass(kw_only=True)
class RestaurantCategory:
    id: str
    name: str
    is_default: bool
    google_category_ids: list[str]


RESTAURANT_CATEGORIES = []


with open("rest_cats.csv", newline="") as f:
    rowiter = csv.DictReader(f)
    for row in rowiter:
        category = next((c for c in RESTAURANT_CATEGORIES if c.name == row["Vivial Category"]), None)

        if category is None:
            category = RestaurantCategory(
                id=uuid4().hex,
                name=row["Vivial Category"],
                is_default=row["Default?"] == "Yes",
                google_category_ids=[]
            )
            RESTAURANT_CATEGORIES.append(category)

        gcid = row["Google ID"]
        if gcid and gcid not in category.google_category_ids:
            category.google_category_ids.append(gcid)


with open("restaurant_category_data.py", "w") as f:
    f.write("RESTAURANT_CATEGORIES = [\n")
    for cat in RESTAURANT_CATEGORIES:
        f.writelines([
            "    RestaurantCategory(\n",
            f"""        id="{cat.id}",\n""",
            f"""        name="{cat.name}",\n""",
            f"""        is_default={cat.is_default},\n""",
            f"""        google_category_ids={cat.google_category_ids},\n""",
            "    ),\n"
        ])
    f.write("]\n")
