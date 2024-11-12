import enum
from datetime import datetime
from typing import Annotated
from uuid import UUID

import strawberry

from eave.core import database
from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.resolvers.outing import MOCK_OUTING, create_outing_plan
from eave.core.graphql.types.outing import (
    Outing,
    OutingBudget,
)
from eave.core.graphql.types.user import UserInput
from eave.core.orm.survey import SurveyOrm
from eave.stdlib.exceptions import ValidationError
from eave.stdlib.logging import LOGGER


@strawberry.input
class PlanOutingInput:
    visitor_id: UUID
    group: list[UserInput]
    start_time: datetime
    search_area_ids: list[UUID]
    budget: OutingBudget
    headcount: int


@strawberry.enum
class PlanOutingErrorCode(enum.Enum):
    START_TIME_TOO_SOON = enum.auto()
    START_TIME_TOO_LATE = enum.auto()
    ONE_SEARCH_REGION_REQUIRED = enum.auto()


@strawberry.type
class PlanOutingSuccess:
    outing: Outing


@strawberry.type
class PlanOutingError:
    error_code: PlanOutingErrorCode


PlanOutingResult = Annotated[PlanOutingSuccess | PlanOutingError, strawberry.union("PlanOutingResult")]


async def plan_outing_mutation(
    *,
    info: strawberry.Info[GraphQLContext],
    input: PlanOutingInput,
) -> PlanOutingResult:
    return PlanOutingSuccess(outing=MOCK_OUTING)

    try:
        async with database.async_session.begin() as db_session:
            survey = SurveyOrm.build(
                visitor_id=input.visitor_id,
                start_time=input.start_time,
                search_area_ids=input.search_area_ids,
                budget=input.budget,
                headcount=input.headcount,
                account_id=info.context.authenticated_account_id,
            )
            await survey.save(session=db_session)
    except ValidationError as e:
        LOGGER.exception(e)
        # TODO: we can't differentiate validation errors well/at all w/ current validation logic
        return PlanOutingError(error_code=PlanOutingErrorCode.ONE_SEARCH_REGION_REQUIRED)

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
            budget=survey.budget,
            headcount=survey.headcount,
            # TODO: remaining fields not available in curr ctx
            activity=None,
            activity_start_time=None,
            restaurant=None,
            restaurant_arrival_time=None,
            driving_time="",
        )
    )
