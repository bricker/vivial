import enum
from datetime import datetime
from typing import Annotated
from uuid import UUID

import strawberry

from eave.core import database
from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.resolvers.mutations.helpers.create_outing import create_outing
from eave.core.graphql.types.outing import (
    Outing,
    OutingPreferencesInput,
)
from eave.core.graphql.validators.time_bounds_validator import start_time_too_far_away, start_time_too_soon
from eave.core.orm.account import AccountOrm
from eave.core.orm.survey import SurveyOrm
from eave.core.shared.enums import OutingBudget
from eave.stdlib.time import LOS_ANGELES_TIMEZONE


@strawberry.input
class PlanOutingInput:
    group_preferences: list[OutingPreferencesInput]
    start_time: datetime
    search_area_ids: list[UUID]
    budget: OutingBudget
    headcount: int
    excluded_eventbrite_event_ids: list[str] | None
    excluded_google_place_ids: list[str] | None
    excluded_evergreen_activity_ids: list[UUID] | None
    is_reroll: bool = False


@strawberry.type
class PlanOutingSuccess:
    outing: Outing


@strawberry.enum
class PlanOutingFailureReason(enum.Enum):
    START_TIME_TOO_SOON = enum.auto()
    START_TIME_TOO_LATE = enum.auto()


@strawberry.type
class PlanOutingFailure:
    failure_reason: PlanOutingFailureReason


PlanOutingResult = Annotated[PlanOutingSuccess | PlanOutingFailure, strawberry.union("PlanOutingResult")]


async def plan_outing_mutation(
    *,
    info: strawberry.Info[GraphQLContext],
    input: PlanOutingInput,
) -> PlanOutingResult:
    account_id = info.context.get("authenticated_account_id")
    visitor_id = info.context.get("visitor_id")

    if start_time_too_soon(start_time=input.start_time, timezone=LOS_ANGELES_TIMEZONE):
        return PlanOutingFailure(failure_reason=PlanOutingFailureReason.START_TIME_TOO_SOON)

    if start_time_too_far_away(start_time=input.start_time, timezone=LOS_ANGELES_TIMEZONE):
        return PlanOutingFailure(failure_reason=PlanOutingFailureReason.START_TIME_TOO_LATE)

    async with database.async_session.begin() as db_session:
        if account_id:
            account = await AccountOrm.get_one(db_session, account_id)
        else:
            account = None

        survey = SurveyOrm(
            db_session,
            account=account,
            visitor_id=visitor_id,
            start_time_utc=input.start_time,
            timezone=LOS_ANGELES_TIMEZONE,
            search_area_ids=input.search_area_ids,
            budget=input.budget,
            headcount=input.headcount,
        )

    outing = await create_outing(
        individual_preferences=input.group_preferences,
        excluded_eventbrite_event_ids=input.excluded_eventbrite_event_ids,
        excluded_google_place_ids=input.excluded_google_place_ids,
        excluded_evergreen_activity_ids=input.excluded_evergreen_activity_ids,
        visitor_id=visitor_id,
        account=account,
        survey=survey,
        is_reroll=input.is_reroll,
    )

    return PlanOutingSuccess(outing=outing)
