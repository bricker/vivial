from uuid import UUID
from datetime import datetime
import strawberry

from eave.core.graphql.types.outing import Outing
from eave.core.orm.booking import BookingOrm


@strawberry.type
class Booking:
    id: UUID
    account_id: UUID
    reserver_details_id: UUID

    @classmethod
    def from_orm(cls, orm: BookingOrm) -> "Booking":
        return Booking(
            id=orm.id,
            account_id=orm.account_id,
            reserver_details_id=orm.reserver_details_id,
        )


@strawberry.type
class BookingDetailPeek:
    id: UUID
    activity_start_time: datetime | None
    activity_name: str | None
    restaurant_start_time: datetime | None
    restaurant_name: str | None


@strawberry.type
class BookingDetails(Outing):
    pass
