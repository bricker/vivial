from uuid import UUID

import strawberry

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
