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

    @strawberry.field
    async def billing_portal_url(self) -> str:
        if self.stripe_customer_id:
            session = await stripe.billing_portal.Session.create_async(
                customer=self.stripe_customer_id,
                return_url=f"{SHARED_CONFIG.eave_dashboard_base_url_public}/account",
            )

            return session.url
        else:
            return SHARED_CONFIG.stripe_customer_portal_url
