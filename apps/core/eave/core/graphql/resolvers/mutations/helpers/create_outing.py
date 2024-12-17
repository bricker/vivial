from eave.core import database
from eave.core.analytics import ANALYTICS
from eave.core.graphql.resolvers.mutations.helpers.planner import OutingPlanner
from eave.core.graphql.types.outing import Outing, OutingPreferencesInput
from eave.core.graphql.types.pricing import CostBreakdown
from eave.core.graphql.types.survey import Survey
from eave.core.lib.address import format_address
from eave.core.lib.event_helpers import get_activity
from eave.core.orm.account import AccountOrm
from eave.core.orm.booking import BookingOrm
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
            db_session,
            visitor_id=visitor_id,
            survey=survey,
            account=account,
        )

        cost_breakdown = CostBreakdown()

        if plan.activity and plan.activity_start_time:
            outing_orm.activities.append(
                OutingActivityOrm(
                    db_session,
                    outing=outing_orm,
                    source_id=plan.activity.source_id,
                    source=plan.activity.source,
                    start_time_utc=plan.activity_start_time,
                    timezone=survey.timezone,
                    headcount=survey.headcount,
                )
            )

            if plan.activity.ticket_info:
                cost_breakdown = plan.activity.ticket_info.cost_breakdown * survey.headcount

        if plan.restaurant and plan.restaurant_arrival_time:
            outing_orm.reservations.append(
                OutingReservationOrm(
                    db_session,
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
        cost_breakdown=cost_breakdown,
        survey=Survey.from_orm(survey),
        activity=plan.activity,
        activity_start_time=plan.activity_start_time,
        restaurant=plan.restaurant,
        restaurant_arrival_time=plan.restaurant_arrival_time,
        driving_time=None,  # TODO
    )

    ANALYTICS.track(
        event_name="outing_created",
        account_id=account.id if account else None,
        visitor_id=visitor_id,
        extra_properties={
            "reroll": reroll,
            "outing_id": str(outing.id),
            "restaurant_info": {
                "start_time": outing.restaurant_arrival_time.isoformat() if outing.restaurant_arrival_time else None,
                "category": outing.restaurant.primary_type_name if outing.restaurant else None,
                "accepts_reservations": outing.restaurant.reservable if outing.restaurant else None,
                "address": format_address(outing.restaurant.location.address.to_address(), singleline=True)
                if outing.restaurant
                else None,
            },
            "activity_info": {
                "start_time": outing.activity_start_time.isoformat() if outing.activity_start_time else None,
                "category": outing.activity.category_group.name
                if outing.activity and outing.activity.category_group
                else None,
                "costs": {
                    "total_cents": outing.activity.ticket_info.cost_breakdown.total_cost_cents_internal
                    if outing.activity and outing.activity.ticket_info
                    else None,
                    "fees_cents": outing.activity.ticket_info.cost_breakdown.fee_cents
                    if outing.activity and outing.activity.ticket_info
                    else None,
                    "tax_cents": outing.activity.ticket_info.cost_breakdown.tax_cents
                    if outing.activity and outing.activity.ticket_info
                    else None,
                },
                "address": format_address(outing.activity.venue.location.address.to_address(), singleline=True)
                if outing.activity
                else None,
            },
            "survey_info": {
                "headcount": outing.survey.headcount if outing.survey else None,
                "start_time": outing.survey.start_time.isoformat() if outing.survey else None,
                "regions": [region.name for region in outing.survey.search_regions] if outing.survey else None,
                "budget": outing.survey.budget if outing.survey else None,
            },
        },
    )

    return outing


async def get_total_cost_cents(orm: OutingOrm | BookingOrm) -> int:
    total_cost_cents = 0

    for activity_orm in orm.activities:
        activity = await get_activity(source=activity_orm.source, source_id=activity_orm.source_id)
        if activity and activity.ticket_info:
            total_cost_cents += (activity.ticket_info.cost_breakdown * activity_orm.headcount).total_cost_cents_internal

    return total_cost_cents
