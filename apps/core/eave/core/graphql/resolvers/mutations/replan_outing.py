import enum
from typing import Annotated
from uuid import UUID

import strawberry

from eave.core import database
from eave.core.analytics import ANALYTICS
from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.resolvers.mutations.helpers.create_outing import create_outing
from eave.core.graphql.resolvers.mutations.helpers.time_bounds_validator import (
    StartTimeTooLateError,
    StartTimeTooSoonError,
    validate_time_within_bounds_or_exception,
)
from eave.core.graphql.types.outing import (
    Outing,
    OutingPreferencesInput,
)
from eave.core.orm.account import AccountOrm
from eave.core.orm.outing import OutingOrm
from eave.stdlib.time import LOS_ANGELES_TIMEZONE
from eave.stdlib.util import unwrap


@strawberry.input
class ReplanOutingInput:
    visitor_id: UUID
    outing_id: UUID
    group_preferences: list[OutingPreferencesInput]


@strawberry.type
class ReplanOutingSuccess:
    outing: Outing


@strawberry.enum
class ReplanOutingFailureReason(enum.Enum):
    START_TIME_TOO_SOON = enum.auto()
    START_TIME_TOO_LATE = enum.auto()


@strawberry.type
class ReplanOutingFailure:
    failure_reason: ReplanOutingFailureReason


ReplanOutingResult = Annotated[ReplanOutingSuccess | ReplanOutingFailure, strawberry.union("ReplanOutingResult")]


async def replan_outing_mutation(
    *,
    info: strawberry.Info[GraphQLContext],
    input: ReplanOutingInput,
) -> ReplanOutingResult:
    account_id = unwrap(info.context.get("authenticated_account_id"))

    async with database.async_session.begin() as db_session:
        account = await AccountOrm.get_one(db_session, account_id)

        original_outing = await OutingOrm.get_one(
            db_session,
            input.outing_id,
        )

    # validate that the survey's start time is still within the bounds.
    try:
        validate_time_within_bounds_or_exception(
            start_time=original_outing.survey.start_time_utc, timezone=LOS_ANGELES_TIMEZONE
        )
    except StartTimeTooLateError:
        return ReplanOutingFailure(failure_reason=ReplanOutingFailureReason.START_TIME_TOO_LATE)
    except StartTimeTooSoonError:
        return ReplanOutingFailure(failure_reason=ReplanOutingFailureReason.START_TIME_TOO_SOON)

    new_outing = await create_outing(
        individual_preferences=input.group_preferences,
        visitor_id=input.visitor_id,
        account=account,  # This should not be the original Outing's account ID, because someone else may be rerolling this outing.
        survey=original_outing.survey,
    )

    ANALYTICS.track(
        event_name="outing plan created",
        account_id=account.id if account else None,
        visitor_id=input.visitor_id,
        extra_properties={
            "reroll": True,
        },
    )

    return ReplanOutingSuccess(outing=new_outing)
