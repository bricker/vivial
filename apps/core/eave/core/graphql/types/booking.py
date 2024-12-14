from datetime import datetime
from uuid import UUID

import strawberry

from eave.core.graphql.types.activity import Activity
from eave.core.graphql.types.outing import Outing
from eave.core.graphql.types.restaurant import Restaurant
from eave.core.orm.booking import BookingOrm


@strawberry.type
class Booking:
    id: UUID
    reserver_details_id: UUID

    @classmethod
    def from_orm(cls, orm: BookingOrm) -> "Booking":
        return Booking(
            id=orm.id,
            reserver_details_id=orm.reserver_details_id,
        )


@strawberry.type
class BookingDetailPeek:
    id: UUID
    activity_start_time: datetime | None
    activity_name: str | None
    restaurant_arrival_time: datetime | None
    restaurant_name: str | None
    photo_uri: str | None


@strawberry.type
class BookingDetails(Outing):
    pass
