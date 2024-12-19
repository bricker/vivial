import strawberry

from eave.core.graphql.types.address import GraphQLAddress
from eave.core.graphql.types.search_region import SearchRegion
from eave.core.orm.search_region import SearchRegionOrm
from eave.core.shared.geo import GeoPoint


@strawberry.type
class Location:
    directions_uri: str | None
    coordinates: GeoPoint
    address: GraphQLAddress

    @strawberry.field
    def search_region(self) -> SearchRegion:
        return self.find_closest_search_region()

    def find_closest_search_region(self) -> SearchRegion:
        return SearchRegion.from_orm(SearchRegionOrm.get_closest(point=self.coordinates))
