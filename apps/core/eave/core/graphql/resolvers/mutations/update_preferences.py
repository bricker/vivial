import enum
from typing import Annotated
from uuid import UUID

import strawberry

from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.types.activity import ActivityCategory
from eave.core.graphql.types.preferences import Preferences
from eave.core.graphql.types.restaurant import RestaurantCategory
from eave.core.orm.activity_category import ActivityCategoryOrm
from eave.core.orm.restaurant_category import RestaurantCategoryOrm
from eave.core.shared.errors import ValidationError


@strawberry.input
class UpdatePreferencesInput:
    open_to_bars: bool | None = strawberry.UNSET
    requires_wheelchair_accessibility: bool | None = strawberry.UNSET
    restaurant_category_ids: list[UUID] | None = strawberry.UNSET
    activity_category_ids: list[UUID] | None = strawberry.UNSET


@strawberry.type
class UpdatePreferencesSuccess:
    preferences: Preferences


@strawberry.enum
class UpdatePreferencesFailureReason(enum.Enum):
    VALIDATION_ERRORS = enum.auto()


@strawberry.type
class UpdatePreferencesFailure:
    failure_reason: UpdatePreferencesFailureReason
    validation_errors: list[ValidationError] | None = None


UpdatePreferencesResult = Annotated[
    UpdatePreferencesSuccess | UpdatePreferencesFailure, strawberry.union("UpdatePreferencesResult")
]

MOCK_PREFERENCES = Preferences(
    open_to_bars=True,
    requires_wheelchair_accessibility=True,
    activity_categories=[ActivityCategory.from_orm(ActivityCategoryOrm.all()[0])],
    restaurant_categories=[RestaurantCategory.from_orm(RestaurantCategoryOrm.all()[0])],
)


async def update_preferences_mutation(
    *, info: strawberry.Info[GraphQLContext], input: UpdatePreferencesInput
) -> UpdatePreferencesResult:
    # account_id = unwrap(info.context.authenticated_account_id)
    return UpdatePreferencesSuccess(preferences=MOCK_PREFERENCES)
