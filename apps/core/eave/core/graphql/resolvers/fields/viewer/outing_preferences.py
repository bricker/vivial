import strawberry

from eave.core import database
from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.types.outing_preferences import OutingPreferences
from eave.core.orm.outing_preferences import OutingPreferencesOrm
from eave.stdlib.util import unwrap


async def list_outing_preferences_query(
    *,
    info: strawberry.Info[GraphQLContext],
) -> OutingPreferences:
    account = unwrap(info.context.get("authenticated_account"))

    if not account.outing_preferences:
        return OutingPreferences(
            activity_categories=None,  # Indicates to the client to use the defaults.
            restaurant_categories=None,
        )
    else:
        return OutingPreferences.from_orm(account.outing_preferences)
