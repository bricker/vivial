from datetime import datetime
from uuid import UUID

import strawberry

from eave.core.graphql.types.search_region import SearchRegion
from eave.core.orm.search_region import SearchRegionOrm
from eave.core.orm.survey import SurveyOrm
from eave.core.shared.enums import OutingBudget
from eave.stdlib.typing import JsonObject


@strawberry.type
class Survey:
    id: UUID
    start_time: datetime
    search_regions: list[SearchRegion]
    budget: OutingBudget
    headcount: int

    @classmethod
    def from_orm(cls, orm: SurveyOrm) -> "Survey":
        return Survey(
            id=orm.id,
            start_time=orm.start_time_local,
            budget=orm.budget,
            headcount=orm.headcount,
            search_regions=[
                SearchRegion.from_orm(SearchRegionOrm.one_or_exception(search_region_id=search_region_id))
                for search_region_id in orm.search_area_ids
            ],
        )

    def build_analytics_properties(self) -> JsonObject:
        return {
            "headcount": self.headcount,
            "start_time": self.start_time.isoformat(),
            "regions": [region.name for region in self.search_regions],
            "budget": self.budget,
        }


@strawberry.input
class SurveyInput:
    start_time: datetime
    search_area_ids: list[UUID]
    budget: OutingBudget
    headcount: int
