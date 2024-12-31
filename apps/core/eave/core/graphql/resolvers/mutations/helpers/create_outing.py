from uuid import UUID

from eave.core import database
from eave.core.graphql.resolvers.mutations.helpers.planner import OutingPlanner
from eave.core.graphql.types.outing import Outing, OutingPreferencesInput
from eave.core.graphql.types.survey import Survey
from eave.core.lib.analytics_client import ANALYTICS
from eave.core.orm.account import AccountOrm
from eave.core.orm.outing import OutingActivityOrm, OutingOrm, OutingReservationOrm
from eave.core.orm.survey import SurveyOrm


async def create_outing(
    *,
    individual_preferences: list[OutingPreferencesInput],
    excluded_eventbrite_event_ids: list[str] | None,
    excluded_google_place_ids: list[str] | None,
    excluded_evergreen_activity_ids: list[UUID] | None,
    visitor_id: str | None,
    account: AccountOrm | None,
    survey: SurveyOrm,
    is_reroll: bool,
) -> Outing:
    plan = await OutingPlanner(
        individual_preferences=individual_preferences,
        excluded_eventbrite_event_ids=excluded_eventbrite_event_ids,
        excluded_google_place_ids=excluded_google_place_ids,
        excluded_evergreen_activity_ids=excluded_evergreen_activity_ids,
        survey=survey,
    ).plan()

    async with database.async_session.begin() as db_session:
        outing_orm = OutingOrm(
            db_session,
            visitor_id=visitor_id,
            survey=survey,
            account=account,
        )

        if activity_plan := plan.activity_plan:
            outing_orm.activities.append(
                OutingActivityOrm(
                    db_session,
                    outing=outing_orm,
                    source_id=activity_plan.activity.source_id,
                    source=activity_plan.activity.source,
                    start_time_utc=activity_plan.start_time,
                    timezone=survey.timezone,  # FIXME: This should come from arrival_time,
                    headcount=activity_plan.headcount,
                )
            )

        if reservation := plan.reservation:
            outing_orm.reservations.append(
                OutingReservationOrm(
                    db_session,
                    outing=outing_orm,
                    source_id=reservation.restaurant.source_id,
                    source=reservation.restaurant.source,
                    start_time_utc=reservation.arrival_time,
                    timezone=survey.timezone,  # FIXME: This should come from arrival_time
                    headcount=reservation.headcount,
                )
            )

    gql_survey = Survey.from_orm(survey)

    outing = Outing(
        id=outing_orm.id,
        survey=gql_survey,
        activity_plan=plan.activity_plan,
        reservation=plan.reservation,
    )

    ANALYTICS.track(
        event_name="outing_created",
        account_id=account.id if account else None,
        visitor_id=visitor_id,
        extra_properties={
            "reroll": is_reroll,
            "outing_id": str(outing.id),
            "restaurant_info": plan.reservation.build_analytics_properties() if plan.reservation else None,
            "activity_info": plan.activity_plan.build_analytics_properties() if plan.activity_plan else None,
            "survey_info": gql_survey.build_analytics_properties(),
        },
    )

    return outing
