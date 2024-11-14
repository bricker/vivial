import enum
from datetime import datetime
from typing import Annotated
from uuid import UUID

import strawberry

from eave.core import database
from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.resolvers.fields.outing import MOCK_OUTING
from eave.core.graphql.resolvers.mutations.helpers.create_outing import create_outing_plan
from eave.core.graphql.types.outing import (
    Outing,
    OutingBudget,
)
from eave.core.graphql.types.preferences import PreferencesInput
from eave.core.orm.survey import SurveyOrm
from eave.core.orm.util import StartTimeTooLateError, StartTimeTooSoonError, validate_time_within_bounds_or_exception


@strawberry.input
class PlanOutingInput:
    visitor_id: UUID
    group_preferences: list[PreferencesInput]
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


@strawberry.type
class PlanOutingFailure:
    failure_reason: PlanOutingFailureReason


PlanOutingResult = Annotated[PlanOutingSuccess | PlanOutingFailure, strawberry.union("PlanOutingResult")]


async def plan_outing_mutation(
    *,
    info: strawberry.Info[GraphQLContext],
    input: PlanOutingInput,
) -> PlanOutingResult:
    return PlanOutingSuccess(outing=MOCK_OUTING)

    async with database.async_session.begin() as db_session:
        survey = await SurveyOrm.build(
            visitor_id=input.visitor_id,
            start_time=input.start_time,
            search_area_ids=input.search_area_ids,
            budget=input.budget,
            headcount=input.headcount,
            account_id=info.context.authenticated_account_id,
        ).save(session=db_session)

        try:
            validate_time_within_bounds_or_exception(input.start_time)
        except StartTimeTooLateError:
            return PlanOutingFailure(failure_reason=PlanOutingFailureReason.START_TIME_TOO_LATE)
        except StartTimeTooSoonError:
            return PlanOutingFailure(failure_reason=PlanOutingFailureReason.START_TIME_TOO_SOON)

    outing = await create_outing_plan(
        visitor_id=survey.visitor_id,
        survey=survey,
        account_id=survey.account_id,
        reroll=False,
    )
    return PlanOutingSuccess(
        outing=Outing(
            id=outing.id,
            visitor_id=outing.visitor_id,
            account_id=outing.account_id,
            survey_id=outing.survey_id,
            budget=survey.outing_budget,
            headcount=survey.headcount,
            # TODO: remaining fields not available in curr ctx
            activity=None,
            activity_start_time=None,
            restaurant=None,
            restaurant_arrival_time=None,
            driving_time="",
        )
    )
