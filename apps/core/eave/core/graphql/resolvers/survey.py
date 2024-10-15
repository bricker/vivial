import datetime
from eave.core.graphql.types.outing import Outing
from eave.core.internal import database
from eave.core.internal.orm.outing import OutingOrm
from eave.core.internal.orm.survey import SurveyOrm
import strawberry


async def submit_survey_for_plan_mutation(
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
            start_time=datetime.datetime.fromisoformat(start_time_iso),
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
