from dataclasses import dataclass
from types import MappingProxyType
from uuid import UUID

from eave.core.orm.activity_subcategory import ActivitySubcategoryOrm


@dataclass(kw_only=True, frozen=True)
class ActivityCategoryOrm:
    id: UUID
    name: str

    @classmethod
    def all(cls) -> list["ActivityCategoryOrm"]:
        return list(_ACTIVITY_CATEGORIES_TABLE)

    @classmethod
    def one_or_exception(cls, *, activity_category_id: UUID) -> "ActivityCategoryOrm":
        return _ACTIVITY_CATEGORIES_PK[activity_category_id]

    @property
    def subcategories(self) -> list[ActivitySubcategoryOrm]:
        return ActivitySubcategoryOrm.get_by_category_id(category_id=self.id)


_ACTIVITY_CATEGORIES_TABLE = (
    ActivityCategoryOrm(
        id=UUID("c44d71bc95bd4a5bb66a7a97c68250ec"),
        name="Seasonal & Holiday",
    ),
    ActivityCategoryOrm(
        id=UUID("f3a21e9638d2401ebc290fee6fe44384"),
        name="Food & Drink",
    ),
    ActivityCategoryOrm(
        id=UUID("64064c758d894eac9613f23cb6da6fd1"),
        name="Film, Media & Entertainment",
    ),
    ActivityCategoryOrm(
        id=UUID("68917f14a9354a4382829b43d99c9ba8"),
        name="Music",
    ),
    ActivityCategoryOrm(
        id=UUID("988e0bf142564462985a2657602aad1b"),
        name="Arts & Theater",
    ),
    ActivityCategoryOrm(
        id=UUID("12e3ee96b00641c58e2a6ba3567816d3"),
        name="Hobbies",
    ),
    ActivityCategoryOrm(
        id=UUID("c0f686d1a4da425ab5c060e2b62344fc"),
        name="Fitness & Outdoors",
    ),
)

_ACTIVITY_CATEGORIES_PK = MappingProxyType({cat.id: cat for cat in _ACTIVITY_CATEGORIES_TABLE})
