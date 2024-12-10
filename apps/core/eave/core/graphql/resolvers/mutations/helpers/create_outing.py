from uuid import UUID

from eave.core import database
from eave.core.graphql.resolvers.mutations.helpers.planner import OutingPlanner
from eave.core.graphql.types.outing import Outing, OutingPreferencesInput
from eave.core.orm.outing import OutingOrm
from eave.core.orm.outing import OutingActivityOrm
from eave.core.orm.outing import OutingReservationOrm
from eave.core.orm.survey import SurveyOrm


async def create_outing(
    *,
    individual_preferences: list[OutingPreferencesInput],
    account_id: UUID | None,
    visitor_id: UUID,
    survey: SurveyOrm,
) -> Outing:
    plan = await OutingPlanner(
        individual_preferences=individual_preferences,
        survey=survey,
    ).plan()

    plan.activity.ticket_info

    async with database.async_session.begin() as db_session:
        outing_orm = await OutingOrm(
            visitor_id=visitor_id,
            survey_id=survey.id,
            account_id=account_id,
        ).save(db_session)

        if plan.activity and plan.activity_start_time:
            await OutingActivityOrm(
                outing_id=outing_orm.id,
                source_id=plan.activity.source_id,
                source=plan.activity.source,
                start_time_utc=plan.activity_start_time,
                timezone=survey.timezone,
                headcount=survey.headcount,
            ).save(session=db_session)

        if plan.restaurant and plan.restaurant_arrival_time:
            await OutingReservationOrm(
                outing_id=outing_orm.id,
                source_id=plan.restaurant.source_id,
                source=plan.restaurant.source,
                start_time_utc=plan.restaurant_arrival_time,
                timezone=survey.timezone,
                headcount=survey.headcount,
            ).save(session=db_session)

        outing = Outing(
            id=outing_orm.id,
            headcount=survey.headcount,
            activity=plan.activity,
            activity_start_time=plan.activity_start_time,
            restaurant=plan.restaurant,
            restaurant_arrival_time=plan.restaurant_arrival_time,
            driving_time=None,  # TODO
        )

    return outing
