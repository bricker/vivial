import enum
from typing import Annotated
from uuid import UUID

import strawberry

from eave.core import database
from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.types.outing_preferences import OutingPreferences
from eave.core.orm.account import AccountOrm
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
        account = await AccountOrm.get_one(db_session, account_id)

        if not account.outing_preferences:
            outing_preferences = OutingPreferencesOrm(
                db_session,
                account=account,
                activity_category_ids=None,
                restaurant_category_ids=None,
            )

            # Adding the OutingPreferences to the session is necessary because
            # just setting account.outing_preferences doesn't automatically back-populate.
            # I think it's because it's a one-to-one relationship.
            account.outing_preferences = outing_preferences

        if input.activity_category_ids:
            account.outing_preferences.activity_category_ids = input.activity_category_ids
        if input.restaurant_category_ids:
            account.outing_preferences.restaurant_category_ids = input.restaurant_category_ids

    return UpdateOutingPreferencesSuccess(outing_preferences=OutingPreferences.from_orm(account.outing_preferences))
