import enum
from datetime import datetime
from typing import Annotated
from uuid import UUID, uuid4

import strawberry

from eave.core import database
from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.resolvers.outing import MOCK_OUTING
from eave.core.graphql.types.activity import EventSource
from eave.core.graphql.types.outing import (
    Outing,
    OutingBudget,
)
from eave.core.graphql.types.event_source import EventSource
from eave.core.lib.analytics import ANALYTICS
from eave.core.orm.outing import OutingOrm
from eave.core.orm.outing_activity import OutingActivityOrm
from eave.core.orm.outing_reservation import OutingReservationOrm


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


async def create_outing_plan(
    *,
    visitor_id: UUID,
    survey_id: UUID,
    account_id: UUID | None,
    reroll: bool,
) -> OutingOrm:
    # TODO: actually call the planning function instead
    async with database.async_session.begin() as db_session:
        outing = await OutingOrm.build(
            visitor_id=visitor_id,
            survey_id=survey_id,
            account_id=account_id,
        ).save(db_session)
        _outing_activity = await OutingActivityOrm.build(
            outing_id=outing.id,
            activity_id=str(uuid4()),
            activity_source=EventSource.EVENTBRITE,
            activity_start_time=datetime.now(),
            num_attendees=2,
        ).save(db_session)
        _outing_reservation = await OutingReservationOrm.build(
            outing_id=outing.id,
            reservation_id=str(uuid4()),
            reservation_source=EventSource.GOOGLE_PLACES,
            reservation_start_time=datetime.now(),
            num_attendees=2,
        ).save(db_session)

    ANALYTICS.track(
        event_name="outing plan created",
        account_id=account_id,
        visitor_id=visitor_id,
        extra_properties={
            "reroll": reroll,
        },
    )
    return outing


async def plan_outing_mutation(
    *,
    info: strawberry.Info[GraphQLContext],
    input: PlanOutingInput,
) -> PlanOutingResult:
    # try:
    #     async with database.async_session.begin() as db_session:
    #         search_areas: list[SearchRegionCode] = []
    #         for area_id in search_area_ids:
    #             if region := SearchRegionCode.from_str(area_id):
    #                 search_areas.append(region)
    #         survey = await SurveyOrm.create(
    #             session=db_session,
    #             visitor_id=visitor_id,
    #             start_time=start_time,
    #             search_area_ids=search_areas,
    #             budget=budget,
    #             headcount=headcount,
    #             account_id=None,  # TODO: look for auth attached to request
    #         )
    # except InvalidDataError as e:
    #     LOGGER.exception(e)
    #     return SubmitSurveyError(error_code=SubmitSurveyErrorCode(e.code))

    # outing = await create_outing_plan(
    #     visitor_id=survey.visitor_id,
    #     survey_id=survey.id,
    #     account_id=survey.account_id,
    #     reroll=False,
    # )

    return PlanOutingSuccess(outing=MOCK_OUTING)
