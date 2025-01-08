import enum
from datetime import datetime
from typing import Annotated
from uuid import UUID

import strawberry

from eave.core import database
from eave.core.graphql.context import GraphQLContext, analytics_ctx
from eave.core.graphql.resolvers.mutations.helpers.planner import OutingPlanner
from eave.core.graphql.types.itinerary import ItineraryRefinement, ItinieraryPart
from eave.core.graphql.types.outing import (
    Outing,
    OutingPreferencesInput,
)
from eave.core.graphql.types.survey import Survey
from eave.core.graphql.validators.time_bounds_validator import start_time_too_far_away, start_time_too_soon
from eave.core.lib.analytics_client import ANALYTICS
from eave.core.orm.account import AccountOrm
from eave.core.orm.outing import OutingActivityOrm, OutingOrm, OutingReservationOrm
from eave.core.orm.survey import SurveyOrm
from eave.core.shared.enums import OutingBudget
from eave.stdlib.matched_str_enum import MatchedStrEnum
from eave.stdlib.time import LOS_ANGELES_TIMEZONE

@strawberry.input
class PlanOutingInput:
    group_preferences: list[OutingPreferencesInput]
    start_time: datetime
    search_area_ids: list[UUID]
    budget: OutingBudget
    headcount: int
    is_reroll: bool = False
    excluded_eventbrite_event_ids: list[str] | None = None
    excluded_google_place_ids: list[str] | None = None
    excluded_evergreen_activity_ids: list[UUID] | None = None
    refinement: ItineraryRefinement | None = None


@strawberry.type
class PlanOutingSuccess:
    outing: Outing


@strawberry.enum
class PlanOutingFailureReason(enum.Enum):
    START_TIME_TOO_SOON = enum.auto()
    START_TIME_TOO_LATE = enum.auto()


@strawberry.type
class PlanOutingFailure:
    failure_reason: PlanOutingFailureReason


PlanOutingResult = Annotated[PlanOutingSuccess | PlanOutingFailure, strawberry.union("PlanOutingResult")]

async def plan_outing_mutation(
    *,
    info: strawberry.Info[GraphQLContext],
    input: PlanOutingInput,
) -> PlanOutingResult:
    account_id = info.context.get("authenticated_account_id")
    visitor_id = info.context.get("visitor_id")

    if start_time_too_soon(start_time=input.start_time, timezone=LOS_ANGELES_TIMEZONE):
        return PlanOutingFailure(failure_reason=PlanOutingFailureReason.START_TIME_TOO_SOON)

    if start_time_too_far_away(start_time=input.start_time, timezone=LOS_ANGELES_TIMEZONE):
        return PlanOutingFailure(failure_reason=PlanOutingFailureReason.START_TIME_TOO_LATE)

    async with database.async_session.begin() as db_session:
        if account_id:
            account = await AccountOrm.get_one(db_session, account_id)
        else:
            account = None

        survey = SurveyOrm(
            db_session,
            account=account,
            visitor_id=visitor_id,
            start_time_utc=input.start_time,
            timezone=LOS_ANGELES_TIMEZONE,
            search_area_ids=input.search_area_ids,
            budget=input.budget,
            headcount=input.headcount,
        )

    outing = await _create_outing(
        individual_preferences=input.group_preferences,
        excluded_eventbrite_event_ids=input.excluded_eventbrite_event_ids,
        excluded_google_place_ids=input.excluded_google_place_ids,
        excluded_evergreen_activity_ids=input.excluded_evergreen_activity_ids,
        refinement=input.refinement,
        visitor_id=visitor_id,
        account=account,
        survey=survey,
        is_reroll=input.is_reroll,
        ctx=info.context,
    )

    return PlanOutingSuccess(outing=outing)

async def _create_outing(
    *,
    individual_preferences: list[OutingPreferencesInput],
    excluded_eventbrite_event_ids: list[str] | None,
    excluded_google_place_ids: list[str] | None,
    excluded_evergreen_activity_ids: list[UUID] | None,
    refinement: ItineraryRefinement | None,
    visitor_id: str | None,
    account: AccountOrm | None,
    survey: SurveyOrm,
    is_reroll: bool,
    ctx: GraphQLContext,
) -> Outing:
    itinerary = await OutingPlanner(
        individual_preferences=individual_preferences,
        excluded_eventbrite_event_ids=excluded_eventbrite_event_ids,
        excluded_google_place_ids=excluded_google_place_ids,
        excluded_evergreen_activity_ids=excluded_evergreen_activity_ids,
        refinement=refinement,
        survey=survey,
        ctx=ctx,
    ).plan()

    async with database.async_session.begin() as db_session:
        outing_orm = OutingOrm(
            db_session,
            visitor_id=visitor_id,
            survey=survey,
            account=account,
        )

        if activity_plan := itinerary.activity_plan:
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

        if reservation := itinerary.reservation:
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
        activity_plan=itinerary.activity_plan,
        reservation=itinerary.reservation,
    )

    ANALYTICS.track(
        event_name="outing_created",
        account_id=account.id if account else None,
        visitor_id=visitor_id,
        extra_properties={
            "reroll": is_reroll,
            "outing_id": str(outing.id),
            "restaurant_info": itinerary.reservation.build_analytics_properties() if itinerary.reservation else None,
            "activity_info": itinerary.activity_plan.build_analytics_properties() if itinerary.activity_plan else None,
            "survey_info": gql_survey.build_analytics_properties(),
        },
        ctx=analytics_ctx(ctx),
    )

    return outing
