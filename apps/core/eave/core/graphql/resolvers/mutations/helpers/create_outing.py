from uuid import UUID

from eave.core import database
from eave.core.analytics import ANALYTICS
from eave.core.graphql.resolvers.mutations.helpers.planner import OutingPlanner, ProposedOuting
from eave.core.graphql.types.survey import Survey
from eave.core.orm.account import AccountOrm
from eave.core.orm.outing import OutingOrm
from eave.core.orm.outing_activity import OutingActivityOrm
from eave.core.orm.outing_reservation import OutingReservationOrm
from eave.core.orm.survey import SurveyOrm


async def create_outing(
    *,
    account_id: UUID | None,
    visitor_id: UUID,
    survey: SurveyOrm,
    plan: ProposedOuting,
) -> OutingOrm:
    async with database.async_session.begin() as db_session:
        outing = await OutingOrm.build(
            visitor_id=visitor_id,
            survey_id=survey.id,
            account_id=account_id,
        ).save(db_session)

        if plan.activity and plan.activity_start_time:
            await OutingActivityOrm.build(
                outing_id=outing.id,
                activity_id=plan.activity.id,
                activity_source=plan.activity.source,
                activity_start_time=plan.activity_start_time,
                headcount=survey.headcount,
            ).save(session=db_session)

        if plan.restaurant and plan.restaurant_arrival_time:
            await OutingReservationOrm.build(
                outing_id=outing.id,
                reservation_id=plan.restaurant.id,
                reservation_source=plan.restaurant.source,
                reservation_start_time=plan.restaurant_arrival_time,
                headcount=survey.headcount,
            ).save(session=db_session)

    return outing
