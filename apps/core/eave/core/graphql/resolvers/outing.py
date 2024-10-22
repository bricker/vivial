from datetime import datetime
from uuid import UUID

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
from eave.core.internal.orm.survey import SurveyOrm
from eave.stdlib.util import ensure_uuid


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
        )

        # TODO: actually call the planning function instead
        outing = await OutingOrm.create(
            session=db_session,
            visitor_id=visitor_id,
            survey_id=survey.id,
            account_id=None,
        )

    return SurveySubmitSuccess(
        outing=Outing(
            id=outing.id,
            visitor_id=outing.visitor_id,
            account_id=outing.account_id,
            survey_id=outing.survey_id,
        )
    )


async def replan_outing_mutation(*, info: strawberry.Info, outing_id: UUID) -> ReplanOutingResult:
    async with database.async_session.begin() as db_session:
        original_outing = await OutingOrm.one_or_exception(
            session=db_session,
            params=OutingOrm.QueryParams(id=ensure_uuid(outing_id)),
        )

        # TODO: actually call the planning function instead
        outing = await OutingOrm.create(
            session=db_session,
            visitor_id=original_outing.visitor_id,
            survey_id=original_outing.survey_id,
            account_id=original_outing.account_id,
        )

    return ReplanOutingSuccess(
        outing=Outing(
            id=outing.id,
            visitor_id=outing.visitor_id,
            account_id=outing.account_id,
            survey_id=outing.survey_id,
        )
    )
