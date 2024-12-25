from uuid import UUID

import strawberry

from eave.core.orm.reserver_details import ReserverDetailsOrm


@strawberry.type
class ReserverDetails:
    id: UUID
    first_name: str
    last_name: str
    phone_number: str

    @classmethod
    def from_orm(cls, orm: ReserverDetailsOrm) -> "ReserverDetails":
        return ReserverDetails(
            id=orm.id,
            first_name=orm.first_name,
            last_name=orm.last_name,
            phone_number=orm.phone_number,
        )
