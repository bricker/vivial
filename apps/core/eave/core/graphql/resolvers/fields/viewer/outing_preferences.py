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
from eave.core.graphql.types.restaurant import RestaurantCategory
from eave.core.orm.activity_category_group import ActivityCategoryGroupOrm
from eave.core.orm.activity_category import ActivityCategoryOrm
from eave.core.orm.outing_category_preference import OutingCategoryPreferenceOrm

from eave.stdlib.util import unwrap

from eave.core.orm.outing_general_preference import OutingGeneralPreferenceOrm
from eave.core.orm.restaurant_category import RestaurantCategoryOrm

@strawberry.type
class OutingPreferences:
    food_type_preferences: list[RestaurantCategory]
    activity_type_preferences: list[ActivityCategory]

async def list_outing_preferences_query(
    *,
    info: strawberry.Info[GraphQLContext],
) -> OutingPreferences:
    account_id = unwrap(info.context.get("authenticated_account_id"))

    async with database.async_session.begin() as db_session:
        category_preferences = await db_session.scalars(
            OutingCategoryPreferenceOrm.select(account_id=account_id)
        )

        general_preferences = await db_session.scalar(
            OutingGeneralPreferenceOrm.select(account_id=account_id)
        )
    return OutingPreferences(
        restaurant_type_preferences=[RestaurantCategory.from_orm(RestaurantCategoryOrm.one_or_exception(restaurant_category_id=category_preference.category_id)) for category_preference in category_preferences if category_preference.category_type == "restaurant"],
        activity_type_preferences=[ActivityCategory.from_orm(ActivityCategoryOrm.one_or_exception(activity_category_id=category_preference.category_id)) for category_preference in category_preferences if category_preference.category_type == "activity"],
    )
