import enum
from typing import Annotated
from uuid import UUID

from eave.stdlib.exceptions import StartTimeTooLateError, StartTimeTooSoonError, ValidationError
from eave.stdlib.logging import LOGGER
import strawberry

from eave.core import database
from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.resolvers.outing import MOCK_OUTING, create_outing_plan
from eave.core.graphql.types.outing import (
    Outing,
)
from eave.core.orm.outing import OutingOrm
from eave.core.orm.survey import SurveyOrm
from eave.core.orm.util import validate_time_within_bounds_or_exception


@strawberry.input
class ReplanOutingInput:
    visitor_id: UUID
    outing_id: UUID


@strawberry.enum
class ReplanOutingErrorCode(enum.Enum):
    START_TIME_TOO_SOON = enum.auto()
    START_TIME_TOO_LATE = enum.auto()


@strawberry.type
class ReplanOutingSuccess:
    outing: Outing


@strawberry.type
class ReplanOutingError:
    error_code: ReplanOutingErrorCode


ReplanOutingResult = Annotated[ReplanOutingSuccess | ReplanOutingError, strawberry.union("ReplanOutingResult")]


async def replan_outing_mutation(
    *,
    info: strawberry.Info[GraphQLContext],
    input: ReplanOutingInput,
) -> ReplanOutingResult:
    return ReplanOutingSuccess(outing=MOCK_OUTING)

    try:
        async with database.async_session.begin() as db_session:
            original_outing = await OutingOrm.get_one(
                session=db_session,
                id=input.outing_id,
            )
            survey = await SurveyOrm.get_one(
                session=db_session,
                id=original_outing.survey_id,
            )

            validate_time_within_bounds_or_exception(survey.start_time)

        outing = await create_outing_plan(
            visitor_id=input.visitor_id,
            survey=survey,
            account_id=original_outing.account_id,  # TODO: this is wrong; look for any auth attached to the request instead
            reroll=True,
        )
    except ValidationError as e:
        LOGGER.exception(e)
        return ReplanOutingError(error_code=ReplanOutingErrorCode(e.code))
    except StartTimeTooLateError as e:
        LOGGER.exception(e)
        return ReplanOutingError(error_code=ReplanOutingErrorCode.START_TIME_TOO_LATE)
    except StartTimeTooSoonError as e:
        LOGGER.exception(e)
        return ReplanOutingError(error_code=ReplanOutingErrorCode.START_TIME_TOO_SOON)

    return ReplanOutingSuccess(
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
