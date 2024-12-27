from datetime import datetime
from uuid import UUID

import strawberry

from eave.core.graphql.types.itinerary import Itinerary
from eave.core.graphql.types.reserver_details import ReserverDetails
from eave.core.orm.booking import BookingOrm
from eave.core.shared.enums import BookingState


@strawberry.type
class Booking:
    id: UUID
    reserver_details: ReserverDetails | None
    state: BookingState

    @classmethod
    def from_orm(cls, orm: BookingOrm) -> "Booking":
        return Booking(
            id=orm.id,
            reserver_details=ReserverDetails.from_orm(orm.reserver_details) if orm.reserver_details else None,
            state=orm.state,
        )


@strawberry.type
class BookingDetailsPeek:
    id: UUID
    activity_start_time: datetime | None
    activity_name: str | None
    restaurant_arrival_time: datetime | None
    restaurant_name: str | None
    photo_uri: str | None
    state: BookingState


@strawberry.type
class BookingDetails(Itinerary):
    state: BookingState
