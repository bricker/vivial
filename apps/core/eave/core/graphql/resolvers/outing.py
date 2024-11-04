from datetime import datetime
from uuid import UUID

import strawberry

from eave.core.graphql.types.outing import (
    Outing,
    ReplanOutingError,
    ReplanOutingErrorCode,
    ReplanOutingResult,
    ReplanOutingSuccess,
    SubmitSurveyError,
    SubmitSurveyErrorCode,
    SubmitSurveyResult,
    SubmitSurveySuccess,
)
from eave.core.internal import database
from eave.core.internal.orm.outing import OutingOrm
from eave.core.internal.orm.outing_activity import OutingActivityOrm
from eave.core.internal.orm.outing_reservation import OutingReservationOrm
from eave.core.internal.orm.survey import SurveyOrm
from eave.core.internal.orm.util import validate_time_within_bounds_or_exception
from eave.core.outing.models.search_region_code import SearchRegionCode
from eave.core.outing.planner import Outing as OutingPlanGenerator
from eave.stdlib.exceptions import InvalidDataError, StartTimeTooLateError, StartTimeTooSoonError
from eave.stdlib.logging import LOGGER


async def create_outing_plan(
    visitor_id: UUID,
    survey: SurveyOrm,
    account_id: UUID | None,
) -> OutingOrm:
    # TODO: fetch user preferences
    # async with database.async_session.begin() as db_session:
    #     account = await AccountOrm.one_or_exception(
    #         session=db_session,
    #         params=AccountOrm.QueryParams(id=account_id),
    #     )

    planner = OutingPlanGenerator(
        group=[],  # TODO: pass user preferences
        constraints=survey,
    )
    plan = await planner.plan()

    async with database.async_session.begin() as db_session:
        outing = await OutingOrm.create(
            session=db_session,
            visitor_id=visitor_id,
            survey_id=survey.id,
            account_id=account_id,
        )

        if plan.activity:
            activity_id = None
            # an activity can be either an event or a restaurant (place)
            # so we have to check both `event` and `place` fields
            if plan.activity.event and (event_id := plan.activity.event.get("id")):
                activity_id = event_id
            elif plan.activity.place:
                activity_id = plan.activity.place.id

            if activity_id:
                await OutingActivityOrm.create(
                    session=db_session,
                    outing_id=outing.id,
                    activity_id=activity_id,
                    activity_source=plan.activity.source,
                    activity_start_time=plan.activity.start_time,
                    num_attendees=survey.headcount,
                )

        if plan.restaurant and plan.restaurant.place:
            await OutingReservationOrm.create(
                session=db_session,
                outing_id=outing.id,
                reservation_id=plan.restaurant.place.id,
                reservation_source=plan.restaurant.source,
                reservation_start_time=plan.restaurant.start_time,
                num_attendees=survey.headcount,
            )
    return outing


async def submit_survey_mutation(
    *,
    info: strawberry.Info,
    visitor_id: UUID,
    start_time: datetime,
    search_area_ids: list[str],
    budget: int,
    headcount: int,
) -> SubmitSurveyResult:
    try:
        async with database.async_session.begin() as db_session:
            search_areas: list[SearchRegionCode] = []
            for area_id in search_area_ids:
                if region := SearchRegionCode.from_str(area_id):
                    search_areas.append(region)
            survey = await SurveyOrm.create(
                session=db_session,
                visitor_id=visitor_id,
                start_time=start_time,
                search_area_ids=search_areas,
                budget=budget,
                headcount=headcount,
                account_id=None,  # TODO: look for auth attached to request
            )
    except InvalidDataError as e:
        LOGGER.exception(e)
        return SubmitSurveyError(error_code=SubmitSurveyErrorCode(e.code))

    outing = await create_outing_plan(
        visitor_id=survey.visitor_id,
        survey=survey,
        account_id=survey.account_id,
    )

    return SubmitSurveySuccess(
        outing=Outing(
            id=outing.id,
            visitor_id=outing.visitor_id,
            account_id=outing.account_id,
            survey_id=outing.survey_id,
        )
    )


async def replan_outing_mutation(
    *,
    info: strawberry.Info,
    visitor_id: UUID,
    outing_id: UUID,
) -> ReplanOutingResult:
    try:
        async with database.async_session.begin() as db_session:
            original_outing = await OutingOrm.one_or_exception(
                session=db_session,
                params=OutingOrm.QueryParams(id=outing_id),
            )
            survey = await SurveyOrm.one_or_exception(
                session=db_session, params=SurveyOrm.QueryParams(id=original_outing.survey_id)
            )

            validate_time_within_bounds_or_exception(survey.start_time)

        outing = await create_outing_plan(
            visitor_id=visitor_id,
            survey=survey,
            account_id=original_outing.account_id,  # TODO: this is wrong; look for any auth attached to the request instead
        )
    except InvalidDataError as e:
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
        )
    )
