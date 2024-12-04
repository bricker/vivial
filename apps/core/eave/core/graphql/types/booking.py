from uuid import UUID

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
class BookingDetails(Outing):
    pass
