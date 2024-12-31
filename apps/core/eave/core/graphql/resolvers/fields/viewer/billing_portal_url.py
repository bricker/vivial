import strawberry
import stripe

from eave.core import database
from eave.core.graphql.context import GraphQLContext
from eave.core.orm.account import AccountOrm
from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.util import unwrap


async def get_billing_portal_url_query(*, info: strawberry.Info[GraphQLContext]) -> str:
    account_id = unwrap(info.context.get("authenticated_account_id"))

    async with database.async_session.begin() as db_session:
        account_orm = await AccountOrm.get_one(db_session, account_id)

    if account_orm.stripe_customer_id:
        configuration = await stripe.billing_portal.Configuration.create_async(
            features={
                "invoice_history": {
                    "enabled": False,
                },
                "customer_update": {
                    "enabled": False,
                },
                "payment_method_update": {
                    "enabled": True,
                },
            },
        )

        session = await stripe.billing_portal.Session.create_async(
            customer=account_orm.stripe_customer_id,
            return_url=f"{SHARED_CONFIG.eave_dashboard_base_url_public}/account",
            configuration=configuration.id,
        )

        return session.url
    else:
        return SHARED_CONFIG.stripe_customer_portal_url
