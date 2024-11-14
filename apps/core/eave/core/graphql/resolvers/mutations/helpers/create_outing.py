from uuid import UUID

from eave.core import database
from eave.core.analytics import ANALYTICS
from eave.core.graphql.resolvers.mutations.helpers.planner import OutingPlanner
from eave.core.graphql.types.survey import Survey
from eave.core.orm.outing import OutingOrm
from eave.core.orm.outing_activity import OutingActivityOrm
from eave.core.orm.outing_reservation import OutingReservationOrm
from eave.core.orm.survey import SurveyOrm


async def create_outing_plan(
    *,
    visitor_id: UUID,
    survey: SurveyOrm,
    account_id: UUID | None,
    reroll: bool,
) -> OutingOrm:
    # TODO: fetch user preferences
    # async with database.async_session.begin() as db_session:
    #     account = await AccountOrm.one_or_exception(
    #         session=db_session,
    #         params=AccountOrm.QueryParams(id=account_id),
    #     )

    planner = OutingPlanner(
        group=[],  # TODO: pass user preferences
        constraints=Survey.from_orm(survey),
    )
    plan = await planner.plan()

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
                num_attendees=survey.headcount,
            ).save(session=db_session)

        if plan.restaurant and plan.restaurant_arrival_time:
            await OutingReservationOrm.build(
                outing_id=outing.id,
                reservation_id=plan.restaurant.id,
                reservation_source=plan.restaurant.source,
                reservation_start_time=plan.restaurant_arrival_time,
                num_attendees=survey.headcount,
            ).save(session=db_session)

    ANALYTICS.track(
        event_name="outing plan created",
        account_id=account_id,
        visitor_id=visitor_id,
        extra_properties={
            "reroll": reroll,
        },
    )
    return outing
