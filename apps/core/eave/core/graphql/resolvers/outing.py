from datetime import datetime
from uuid import UUID, uuid4

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
from eave.core.outing.models.search_region import SearchRegionCode
from eave.stdlib.core_api.models.enums import ActivitySource, ReservationSource
from eave.stdlib.exceptions import InvalidDataError, StartTimeTooLateError, StartTimeTooSoonError
from eave.stdlib.logging import LOGGER


async def create_outing_plan(
    visitor_id: UUID,
    survey_id: UUID,
    account_id: UUID | None,
) -> OutingOrm:
    # TODO: actually call the planning function instead
    async with database.async_session.begin() as db_session:
        outing = await OutingOrm.create(
            session=db_session,
            visitor_id=visitor_id,
            survey_id=survey_id,
            account_id=account_id,
        )
        _outing_activity = await OutingActivityOrm.create(
            session=db_session,
            outing_id=outing.id,
            activity_id=str(uuid4()),
            activity_source=ActivitySource.EVENTBRITE,
            activity_start_time=datetime.now(),
            num_attendees=2,
        )
        _outing_reservation = await OutingReservationOrm.create(
            session=db_session,
            outing_id=outing.id,
            reservation_id=str(uuid4()),
            reservation_source=ReservationSource.GOOGLE_PLACES,
            reservation_start_time=datetime.now(),
            num_attendees=2,
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
        survey_id=survey.id,
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
            survey_id=original_outing.survey_id,
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
