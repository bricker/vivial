from datetime import datetime

import strawberry

from eave.core.graphql.types.outing import Outing
from eave.core.internal import database
from eave.core.internal.orm.outing import OutingOrm
from eave.core.internal.orm.survey import SurveyOrm
from eave.stdlib.util import ensure_uuid


async def outing_from_survey_mutation(
    *,
    info: strawberry.Info,
    visitor_id: str,
    start_time_iso: str,
    search_area_ids: list[str],
    budget: int,
    headcount: int,
) -> Outing:
    async with database.async_session.begin() as db_session:
        survey = await SurveyOrm.create(
            session=db_session,
            visitor_id=visitor_id,
            start_time=datetime.fromisoformat(start_time_iso),
            search_area_ids=search_area_ids,
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

    return Outing(
        id=outing.id,
        visitor_id=outing.visitor_id,
        account_id=outing.account_id,
        survey_id=outing.survey_id,
    )


async def replan_outing_mutation(*, info: strawberry.Info, outing_id: str) -> Outing:
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

    return Outing(
        id=outing.id,
        visitor_id=outing.visitor_id,
        account_id=outing.account_id,
        survey_id=outing.survey_id,
    )
