from uuid import UUID

import strawberry
import stripe

from eave.core import database
from eave.core.graphql.types.reserver_details import ReserverDetails
from eave.core.graphql.types.stripe import PaymentMethod
from eave.core.orm.account import AccountOrm

@strawberry.type
class Account:
    id: UUID
    email: str
    stripe_customer_id: str | None

    @classmethod
    def from_orm(cls, orm: AccountOrm) -> "Account":
        return Account(
            id=orm.id,
            email=orm.email,
            stripe_customer_id=orm.stripe_customer_id
        )
