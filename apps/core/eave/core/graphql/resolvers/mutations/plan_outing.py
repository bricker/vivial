import enum
from datetime import datetime
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
from eave.core.orm.survey import SurveyOrm
from eave.core.shared.enums import OutingBudget
from eave.stdlib.time import LOS_ANGELES_TIMEZONE


@strawberry.input
class PlanOutingInput:
    visitor_id: UUID
    group_preferences: list[OutingPreferencesInput]
    start_time: datetime
    search_area_ids: list[UUID]
    budget: OutingBudget
    headcount: int


@strawberry.type
class PlanOutingSuccess:
    outing: Outing


@strawberry.enum
class PlanOutingFailureReason(enum.Enum):
    START_TIME_TOO_SOON = enum.auto()
    START_TIME_TOO_LATE = enum.auto()
    SEARCH_AREA_IDS_EMPTY = enum.auto()


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

    if len(input.search_area_ids) == 0:
        return PlanOutingFailure(failure_reason=PlanOutingFailureReason.SEARCH_AREA_IDS_EMPTY)

    try:
        validate_time_within_bounds_or_exception(start_time=input.start_time, timezone=LOS_ANGELES_TIMEZONE)
    except StartTimeTooLateError:
        return PlanOutingFailure(failure_reason=PlanOutingFailureReason.START_TIME_TOO_LATE)
    except StartTimeTooSoonError:
        return PlanOutingFailure(failure_reason=PlanOutingFailureReason.START_TIME_TOO_SOON)

    async with database.async_session.begin() as db_session:
        survey = await SurveyOrm.build(
            account_id=account_id,
            visitor_id=input.visitor_id,
            start_time_utc=input.start_time,
            timezone=LOS_ANGELES_TIMEZONE,
            search_area_ids=input.search_area_ids,
            budget=input.budget,
            headcount=input.headcount,
        ).save(session=db_session)

    outing = await create_outing(
        individual_preferences=input.group_preferences,
        visitor_id=input.visitor_id,
        survey=survey,
    )

    ANALYTICS.track(
        event_name="outing plan created",
        account_id=account_id,
        visitor_id=input.visitor_id,
        extra_properties={
            "reroll": False,
        },
    )

    return PlanOutingSuccess(outing=outing)
