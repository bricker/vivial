from datetime import datetime
from uuid import UUID, uuid4

import strawberry

from eave.core.areas.search_region_code import SearchRegionCode
from eave.core.graphql.types.outing import (
    Outing,
    ReplanOutingResult,
    ReplanOutingSuccess,
    SurveySubmitResult,
    SurveySubmitSuccess,
)
from eave.core.internal import database
from eave.core.internal.orm.outing import OutingOrm
from eave.core.internal.orm.outing_activity import OutingActivityOrm
from eave.core.internal.orm.outing_reservation import OutingReservationOrm
from eave.core.internal.orm.survey import SurveyOrm


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
            activity_datetime=datetime.now(),
            num_attendees=2,
        )
        _outing_reservation = await OutingReservationOrm.create(
            session=db_session,
            outing_id=outing.id,
            reservation_id=str(uuid4()),
            reservation_datetime=datetime.now(),
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
) -> SurveySubmitResult:
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

    outing = await create_outing_plan(
        visitor_id=survey.visitor_id,
        survey_id=survey.id,
        account_id=survey.account_id,
    )

    return SurveySubmitSuccess(
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
    async with database.async_session.begin() as db_session:
        original_outing = await OutingOrm.one_or_exception(
            session=db_session,
            params=OutingOrm.QueryParams(id=outing_id),
        )

    outing = await create_outing_plan(
        visitor_id=visitor_id,
        survey_id=original_outing.survey_id,
        account_id=original_outing.account_id,  # TODO: this is wrong; look for any auth attached to the request instead
    )

    return ReplanOutingSuccess(
        outing=Outing(
            id=outing.id,
            visitor_id=outing.visitor_id,
            account_id=outing.account_id,
            survey_id=outing.survey_id,
        )
    )
