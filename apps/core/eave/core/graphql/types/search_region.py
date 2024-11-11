from uuid import UUID

import strawberry

from eave.core.orm.search_region import SearchRegionOrm


@strawberry.type
class SearchRegion:
    id: UUID
    name: str

    @classmethod
    def from_orm(cls, orm: SearchRegionOrm) -> "SearchRegion":
        return SearchRegion(
            id=orm.id,
            name=orm.name,
        )
