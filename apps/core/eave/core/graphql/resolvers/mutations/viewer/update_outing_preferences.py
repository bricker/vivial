import enum
from typing import Annotated
from uuid import UUID

import strawberry

from eave.core import database
from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.types.activity import ActivityCategory, ActivityCategoryGroup
from eave.core.graphql.types.outing_preferences import OutingPreferences
from eave.core.graphql.types.restaurant import RestaurantCategory
from eave.core.orm.activity_category import ActivityCategoryOrm
from eave.core.orm.activity_category_group import ActivityCategoryGroupOrm
from eave.core.orm.outing_category_preference import OutingCategoryPreferenceOrm
from eave.core.orm.restaurant_category import RestaurantCategoryOrm
from eave.core.shared.errors import ValidationError

from eave.stdlib.util import unwrap

@strawberry.input
class UpdateOutingPreferencesInput:
    restaurant_category_ids: list[UUID] | None = strawberry.UNSET
    activity_category_ids: list[UUID] | None = strawberry.UNSET


@strawberry.type
class UpdateOutingPreferencesSuccess:
    outing_preferences: OutingPreferences


@strawberry.enum
class UpdateOutingPreferencesFailureReason(enum.Enum):
    VALIDATION_ERRORS = enum.auto()


@strawberry.type
class UpdateOutingPreferencesFailure:
    failure_reason: UpdateOutingPreferencesFailureReason
    validation_errors: list[ValidationError] | None = None


UpdateOutingPreferencesResult = Annotated[
    UpdateOutingPreferencesSuccess | UpdateOutingPreferencesFailure, strawberry.union("UpdateOutingPreferencesResult")
]


async def update_outing_preferences_mutation(
    *, info: strawberry.Info[GraphQLContext], input: UpdateOutingPreferencesInput
) -> UpdateOutingPreferencesResult:
    account_id = unwrap(info.context.get("authenticated_account_id"))

    async with database.async_session.begin() as db_session:
        category_preferences = await db_session.scalars(
            OutingCategoryPreferenceOrm.select(account_id=account_id)
        )

    return UpdateOutingPreferencesSuccess(
        outing_preferences=OutingPreferences.from_orms(category_preferences)
    )
