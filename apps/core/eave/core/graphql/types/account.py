from uuid import UUID

import strawberry
import stripe

from eave.core.orm.account import AccountOrm
from eave.stdlib.config import SHARED_CONFIG


@strawberry.type
class Account:
    id: UUID
    email: str
    stripe_customer_id: str | None

    @classmethod
    def from_orm(cls, orm: AccountOrm) -> "Account":
        return Account(id=orm.id, email=orm.email, stripe_customer_id=orm.stripe_customer_id)
