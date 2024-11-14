import enum
from typing import Annotated
from uuid import UUID

import strawberry

from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.resolvers.fields.outing import MOCK_OUTING
from eave.core.graphql.types.outing import (
    Outing,
)


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
    # try:
    #     async with database.async_session.begin() as db_session:
    #         original_outing = await OutingOrm.one_or_exception(
    #             session=db_session,
    #             params=OutingOrm.QueryParams(id=outing_id),
    #         )
    #         survey = await SurveyOrm.one_or_exception(
    #             session=db_session, params=SurveyOrm.QueryParams(id=original_outing.survey_id)
    #         )

    #         validate_time_within_bounds_or_exception(survey.start_time)

    #     outing = await create_outing_plan(
    #         visitor_id=visitor_id,
    #         survey_id=original_outing.survey_id,
    #         account_id=original_outing.account_id,  # TODO: this is wrong; look for any auth attached to the request instead
    #         reroll=True,
    #     )
    # except InvalidDataError as e:
    #     LOGGER.exception(e)
    #     return ReplanOutingError(error_code=ReplanOutingErrorCode(e.code))
    # except StartTimeTooLateError as e:
    #     LOGGER.exception(e)
    #     return ReplanOutingError(error_code=ReplanOutingErrorCode.START_TIME_TOO_LATE)
    # except StartTimeTooSoonError as e:
    #     LOGGER.exception(e)
    #     return ReplanOutingError(error_code=ReplanOutingErrorCode.START_TIME_TOO_SOON)

    return ReplanOutingSuccess(outing=MOCK_OUTING)
