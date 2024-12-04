import copy
import datetime

import strawberry

from eave.core import database
from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.resolvers.fields.outing import MOCK_OUTING
from eave.core.graphql.types.activity import ActivityCategory, ActivitySubcategory
from eave.core.graphql.types.outing import (
    Outing,
    OutingState,
)
from eave.core.graphql.types.restaurant import RestaurantCategory
from eave.core.orm.activity_category import ActivityCategoryOrm
from eave.core.orm.activity_subcategory import ActivitySubcategoryOrm
from eave.core.orm.outing_category_preference import OutingCategoryPreferenceOrm

from eave.stdlib.util import unwrap

from eave.core.orm.outing_general_preference import OutingGeneralPreferenceOrm
from eave.core.orm.restaurant_category import RestaurantCategoryOrm

@strawberry.type
class OutingPreferences:
    open_to_bars: bool
    requires_wheelchair_accessibility: bool
    food_type_preferences: list[RestaurantCategory]
    activity_type_preferences: list[ActivitySubcategory]

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

    open_to_bars = True
    requires_wheelchair_accessibility = False

    if general_preferences:
        if general_preferences.open_to_bars is not None:
            open_to_bars = general_preferences.open_to_bars
        if general_preferences.requires_wheelchair_accessibility is not None:
            requires_wheelchair_accessibility = general_preferences.requires_wheelchair_accessibility

    return OutingPreferences(
        open_to_bars=open_to_bars,
        requires_wheelchair_accessibility=requires_wheelchair_accessibility,
        food_type_preferences=[RestaurantCategory.from_orm(RestaurantCategoryOrm.one_or_exception(restaurant_category_id=category_preference.category_id)) for category_preference in category_preferences if category_preference.category_type == "restaurant"],
        activity_type_preferences=[ActivitySubcategory.from_orm(ActivitySubcategoryOrm.one_or_exception(activity_subcategory_id=category_preference.category_id)) for category_preference in category_preferences if category_preference.category_type == "activity"],
    )
