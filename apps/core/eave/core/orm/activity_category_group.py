from dataclasses import dataclass
from types import MappingProxyType
from uuid import UUID

from eave.core.orm.activity_category import ActivityCategoryOrm


@dataclass(kw_only=True, frozen=True)
class ActivityCategoryGroupOrm:
    id: UUID
    name: str

    @classmethod
    def all(cls) -> list["ActivityCategoryGroupOrm"]:
        return list(_ACTIVITY_CATEGORY_GROUPS_TABLE)

    @classmethod
    def one_or_exception(cls, *, activity_category_group_id: UUID) -> "ActivityCategoryGroupOrm":
        return _ACTIVITY_CATEGORY_GROUPS_PK[activity_category_group_id]

    @classmethod
    def one_or_none(cls, *, activity_category_group_id: UUID) -> "ActivityCategoryGroupOrm | None":
        return _ACTIVITY_CATEGORY_GROUPS_PK.get(activity_category_group_id)

    @property
    def activity_categories(self) -> list[ActivityCategoryOrm]:
        return ActivityCategoryOrm.get_by_activity_category_group_id(activity_category_group_id=self.id)


_ACTIVITY_CATEGORY_GROUPS_TABLE = (
    ActivityCategoryGroupOrm(
        id=UUID("68917f14a9354a4382829b43d99c9ba8"),
        name="Music",
    ),
    ActivityCategoryGroupOrm(
        id=UUID("988e0bf142564462985a2657602aad1b"),
        name="Arts & theater",
    ),
    ActivityCategoryGroupOrm(
        id=UUID("64064c758d894eac9613f23cb6da6fd1"),
        name="Film, media & entertainment",
    ),
    ActivityCategoryGroupOrm(
        id=UUID("f3a21e9638d2401ebc290fee6fe44384"),
        name="Food & drinks",
    ),
    ActivityCategoryGroupOrm(
        id=UUID("12e3ee96b00641c58e2a6ba3567816d3"),
        name="Hobbies",
    ),
    ActivityCategoryGroupOrm(
        id=UUID("c0f686d1a4da425ab5c060e2b62344fc"),
        name="Fitness & outdoors",
    ),
    ActivityCategoryGroupOrm(
        id=UUID("c44d71bc95bd4a5bb66a7a97c68250ec"),
        name="Seasonal & holiday",
    ),
)

_ACTIVITY_CATEGORY_GROUPS_PK = MappingProxyType({cat.id: cat for cat in _ACTIVITY_CATEGORY_GROUPS_TABLE})
