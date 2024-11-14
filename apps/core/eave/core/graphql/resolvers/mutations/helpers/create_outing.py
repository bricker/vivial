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

        if plan.activity:
            activity_id = None
            # an activity can be either an event or a restaurant (place)
            # so we have to check both `event` and `place` fields
            if plan.activity.event and (event_id := plan.activity.event.get("id")):
                activity_id = event_id
            elif plan.activity.place:
                activity_id = plan.activity.place.id

            if activity_id:
                await OutingActivityOrm.build(
                    outing_id=outing.id,
                    activity_id=activity_id,
                    activity_source=plan.activity.source,
                    activity_start_time=plan.activity.start_time,
                    num_attendees=survey.headcount,
                ).save(session=db_session)

        if plan.restaurant and plan.restaurant.place:
            await OutingReservationOrm.build(
                outing_id=outing.id,
                reservation_id=plan.restaurant.place.id,
                reservation_source=plan.restaurant.source,
                reservation_start_time=plan.restaurant.start_time,
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
