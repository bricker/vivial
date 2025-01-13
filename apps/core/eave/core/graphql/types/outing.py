from uuid import UUID

import strawberry

from eave.core.graphql.types.itinerary import Itinerary


@strawberry.input
class OutingPreferencesInput:
    restaurant_category_ids: list[UUID]
    activity_category_ids: list[UUID]


@strawberry.type
class Outing(Itinerary):
    id: UUID

