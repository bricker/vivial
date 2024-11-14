import strawberry

from eave.core.graphql.types.search_region import SearchRegion
from eave.core.orm.search_region import SearchRegionOrm


async def list_search_regions_query(*, info: strawberry.Info) -> list[SearchRegion]:
    all_search_regions = SearchRegionOrm.all()
    return [SearchRegion.from_orm(orm) for orm in all_search_regions]
