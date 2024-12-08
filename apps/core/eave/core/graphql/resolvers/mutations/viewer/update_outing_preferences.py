import enum
from typing import Annotated
from uuid import UUID

import strawberry

from eave.core import database
from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.types.outing_preferences import OutingPreferences
from eave.core.orm.outing_preferences import OutingPreferencesOrm
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
        outing_preferences = (
            await db_session.scalars(OutingPreferencesOrm.select(account_id=account_id))
        ).one_or_none()

        if not outing_preferences:
            outing_preferences = OutingPreferencesOrm.build(
                account_id=account_id,
                activity_category_ids=None,
                restaurant_category_ids=None,
            )

        if input.activity_category_ids:
            outing_preferences.activity_category_ids = input.activity_category_ids
        if input.restaurant_category_ids:
            outing_preferences.restaurant_category_ids = input.restaurant_category_ids

        await outing_preferences.save(db_session)

    return UpdateOutingPreferencesSuccess(outing_preferences=OutingPreferences.from_orm(outing_preferences))
