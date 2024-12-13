from uuid import UUID

from eave.core import database
from eave.core.analytics import ANALYTICS
from eave.core.graphql.resolvers.mutations.helpers.planner import OutingPlanner
from eave.core.graphql.types.outing import Outing, OutingPreferencesInput
from eave.core.graphql.types.search_region import SearchRegion
from eave.core.graphql.types.survey import Survey
from eave.core.lib.event_helpers import get_closest_search_region_to_point
from eave.core.orm.outing import OutingOrm
from eave.core.orm.outing_activity import OutingActivityOrm
from eave.core.orm.outing_reservation import OutingReservationOrm
from eave.core.orm.search_region import SearchRegionOrm
from eave.core.orm.survey import SurveyOrm


async def create_outing(
    *,
    individual_preferences: list[OutingPreferencesInput],
    visitor_id: UUID,
    survey: SurveyOrm,
    account_id: UUID | None = None,
) -> Outing:
    plan = await OutingPlanner(
        individual_preferences=individual_preferences,
        survey=survey,
    ).plan()

    async with database.async_session.begin() as db_session:
        outing_orm = await OutingOrm.build(
            visitor_id=visitor_id,
            survey_id=survey.id,
        ).save(db_session)

        if plan.activity and plan.activity_start_time:
            await OutingActivityOrm.build(
                outing_id=outing_orm.id,
                source_id=plan.activity.source_id,
                source=plan.activity.source,
                start_time_utc=plan.activity_start_time,
                timezone=survey.timezone,
                headcount=survey.headcount,
            ).save(session=db_session)

        if plan.restaurant and plan.restaurant_arrival_time:
            await OutingReservationOrm.build(
                outing_id=outing_orm.id,
                source_id=plan.restaurant.source_id,
                source=plan.restaurant.source,
                start_time_utc=plan.restaurant_arrival_time,
                timezone=survey.timezone,
                headcount=survey.headcount,
            ).save(session=db_session)

        activity_region = restaurant_region = None
        regions = [SearchRegionOrm.one_or_exception(search_region_id=area_id) for area_id in survey.search_area_ids]
        if plan.activity:
            activity_region = get_closest_search_region_to_point(
                regions=regions, point=plan.activity.venue.location.coordinates
            )
        if plan.restaurant:
            restaurant_region = get_closest_search_region_to_point(
                regions=regions, point=plan.restaurant.location.coordinates
            )

        outing = Outing(
            id=outing_orm.id,
            survey=Survey.from_orm(survey),
            activity=plan.activity,
            activity_start_time=plan.activity_start_time,
            restaurant=plan.restaurant,
            restaurant_arrival_time=plan.restaurant_arrival_time,
            driving_time=None,  # TODO
            activity_region=SearchRegion.from_orm(activity_region) if activity_region else None,
            restaurant_region=SearchRegion.from_orm(restaurant_region) if restaurant_region else None,
        )

    ANALYTICS.track(
        event_name="outing plan created",
        account_id=account_id,
        visitor_id=visitor_id,
        extra_properties={
            "reroll": True,
        },
    )

    return outing
