from uuid import UUID

import strawberry

from eave.core.orm.account import AccountOrm


@strawberry.type
class Account:
    id: UUID
    email: str

    @classmethod
    def from_orm(cls, orm: AccountOrm) -> "Account":
        return Account(
            id=orm.id,
            email=orm.email,
        )
