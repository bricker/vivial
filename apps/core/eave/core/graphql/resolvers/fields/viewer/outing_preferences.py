import copy
import datetime

import strawberry

from eave.core import database
from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.resolvers.fields.outing import MOCK_OUTING
from eave.core.graphql.types.activity import ActivityCategoryGroup, ActivityCategory
from eave.core.graphql.types.outing import (
    Outing,
    OutingState,
)
from eave.core.graphql.types.outing_preferences import OutingPreferences
from eave.core.graphql.types.restaurant import RestaurantCategory
from eave.core.orm.activity_category_group import ActivityCategoryGroupOrm
from eave.core.orm.activity_category import ActivityCategoryOrm
from eave.core.orm.outing_preferences import OutingPreferencesOrm

from eave.stdlib.util import unwrap

from eave.core.orm.restaurant_category import RestaurantCategoryOrm

async def list_outing_preferences_query(
    *,
    info: strawberry.Info[GraphQLContext],
) -> OutingPreferences:
    account_id = unwrap(info.context.get("authenticated_account_id"))

    async with database.async_session.begin() as db_session:
        category_preferences = (await db_session.scalars(
            OutingPreferencesOrm.select(account_id=account_id)
        )).one_or_none()

        if not category_preferences:
            return OutingPreferences(
                open_to_bars=True, # the default value
                activity_categories=None, # Indicates to the client to use the defaults.
                restaurant_categories=None,
            )
        else:
            return OutingPreferences.from_orm(category_preferences)
