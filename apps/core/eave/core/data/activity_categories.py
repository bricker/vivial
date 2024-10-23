from dataclasses import dataclass
import json


@dataclass
class ActivityCategory:
    name: str
    parent_category_id: str
    eventbrite_category_id: str
    eventbrite_subcategory_id: str

with open("activity_categories.json") as f:
    AREAS = [ActivityCategory(**j) for j in json.loads(f.read())]
