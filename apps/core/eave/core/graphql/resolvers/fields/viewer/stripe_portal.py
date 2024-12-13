import strawberry
import stripe

from eave.core import database
from eave.core.graphql.types.stripe_portal import StripePortal
from eave.core.orm.account import AccountOrm
from eave.stdlib.config import SHARED_CONFIG
from eave.core.graphql.context import GraphQLContext
from eave.stdlib.util import unwrap


async def get_stripe_portal_query(*, info: strawberry.Info[GraphQLContext]) -> StripePortal:
    account_id = unwrap(info.context.get("authenticated_account_id"))

    async with database.async_session.begin() as db_session:
        account = await AccountOrm.get_one(
            session=db_session,
            id=account_id,
        )

    # TODO: get customer ID from account?

    session = stripe.billing_portal.Session.create(
        customer="TOODO customer ID from somewhere..",
        return_url=f"{SHARED_CONFIG.eave_dashboard_base_url_public}/account",
    )

    return StripePortal(url=session.url)
