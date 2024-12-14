
from eave.core import database
from eave.core.analytics import ANALYTICS
from eave.core.graphql.resolvers.mutations.helpers.planner import OutingPlanner
from eave.core.graphql.types.outing import Outing, OutingPreferencesInput
from eave.core.graphql.types.survey import Survey
from eave.core.lib.event_helpers import get_activity
from eave.core.orm.account import AccountOrm
from eave.core.orm.outing import OutingActivityOrm, OutingOrm, OutingReservationOrm
from eave.core.orm.survey import SurveyOrm


async def create_outing(
    *,
    individual_preferences: list[OutingPreferencesInput],
    visitor_id: str | None,
    account: AccountOrm | None,
    survey: SurveyOrm,
    reroll: bool,
) -> Outing:
    plan = await OutingPlanner(
        individual_preferences=individual_preferences,
        survey=survey,
    ).plan()

    async with database.async_session.begin() as db_session:
        outing_orm = OutingOrm(
            visitor_id=visitor_id,
            survey=survey,
            account=account,
        )
        db_session.add(outing_orm)

        if plan.activity and plan.activity_start_time:
            outing_orm.activities.append(
                OutingActivityOrm(
                    outing=outing_orm,
                    source_id=plan.activity.source_id,
                    source=plan.activity.source,
                    start_time_utc=plan.activity_start_time,
                    timezone=survey.timezone,
                    headcount=survey.headcount,
                )
            )

        if plan.restaurant and plan.restaurant_arrival_time:
            outing_orm.reservations.append(
                OutingReservationOrm(
                    outing=outing_orm,
                    source_id=plan.restaurant.source_id,
                    source=plan.restaurant.source,
                    start_time_utc=plan.restaurant_arrival_time,
                    timezone=survey.timezone,
                    headcount=survey.headcount,
                )
            )

    outing = Outing(
        id=outing_orm.id,
        headcount=survey.headcount,
        activity=plan.activity,
        activity_start_time=plan.activity_start_time,
        restaurant=plan.restaurant,
        restaurant_arrival_time=plan.restaurant_arrival_time,
        driving_time=None,  # TODO
        survey=Survey.from_orm(outing_orm.survey),
    )

    ANALYTICS.track(
        event_name="outing plan created",
        account_id=account.id if account else None,
        visitor_id=visitor_id,
        extra_properties={
            "reroll": reroll,
        },
    )

    return outing


async def get_outing_total_cost_cents(*, outing_orm: OutingOrm) -> int:
    total_cost_cents = 0

    for outing_activity_orm in outing_orm.activities:
        activity = await get_activity(source=outing_activity_orm.source, source_id=outing_activity_orm.source_id)
        if activity:
            total_cost_cents += activity.pricing.total_cost_cents_internal

    return total_cost_cents
