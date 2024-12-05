import enum
from typing import Annotated
from uuid import UUID

import strawberry

from eave.core import database
from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.resolvers.fields.outing import MOCK_OUTING
from eave.core.graphql.resolvers.mutations.helpers.create_outing import create_outing_plan
from eave.core.graphql.types.outing import (
    Outing,
)
from eave.core.orm.outing import OutingOrm
from eave.core.orm.survey import SurveyOrm
from eave.core.orm.util import StartTimeTooLateError, StartTimeTooSoonError, validate_time_within_bounds_or_exception


@strawberry.input
class ReplanOutingInput:
    visitor_id: UUID
    outing_id: UUID


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
    return ReplanOutingSuccess(outing=MOCK_OUTING)

    async with database.async_session.begin() as db_session:
        original_outing = await OutingOrm.get_one(
            session=db_session,
            id=input.outing_id,
        )
        survey = await SurveyOrm.get_one(
            session=db_session,
            id=original_outing.survey_id,
        )

    # validate that the survey's start time is still within the bounds.
    try:
        validate_time_within_bounds_or_exception(survey.start_time)
    except StartTimeTooLateError:
        return ReplanOutingFailure(failure_reason=ReplanOutingFailureReason.START_TIME_TOO_LATE)
    except StartTimeTooSoonError:
        return ReplanOutingFailure(failure_reason=ReplanOutingFailureReason.START_TIME_TOO_SOON)

    outing = await create_outing_plan(
        visitor_id=input.visitor_id,
        survey=survey,
        account_id=info.context.get("authenticated_account_id"),
        reroll=True,
    )

    return ReplanOutingSuccess(
        outing=Outing(
            id=outing.id,
            headcount=survey.headcount,
            # TODO: remaining fields not available in curr ctx
            activity=None,
            activity_start_time=None,
            restaurant=None,
            restaurant_arrival_time=None,
            driving_time="",
        )
    )
