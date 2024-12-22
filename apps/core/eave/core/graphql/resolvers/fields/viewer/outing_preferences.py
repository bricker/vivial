import strawberry

from eave.core import database
from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.types.outing_preferences import OutingPreferences
from eave.core.orm.account import AccountOrm
from eave.stdlib.util import unwrap


async def get_outing_preferences_query(
    *,
    info: strawberry.Info[GraphQLContext],
) -> OutingPreferences:
    account_id = unwrap(info.context.get("authenticated_account_id"))

    async with database.async_session.begin() as session:
        account = await AccountOrm.get_one(session, account_id)

    if not account.outing_preferences:
        return OutingPreferences(
            activity_categories=None,  # Indicates to the client to use the defaults.
            restaurant_categories=None,
        )
    else:
        return OutingPreferences.from_orm(account.outing_preferences)
