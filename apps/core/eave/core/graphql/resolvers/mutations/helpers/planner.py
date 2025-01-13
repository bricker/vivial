import dataclasses
import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import func

import eave.core.database
from eave.core.graphql.context import GraphQLContext, LogContext, log_ctx
from eave.core.graphql.types.activity import Activity, ActivityPlan
from eave.core.graphql.types.cost_breakdown import CostBreakdown
from eave.core.graphql.types.outing import OutingPreferencesInput
from eave.core.graphql.types.restaurant import Reservation, Restaurant
from eave.core.graphql.types.survey import Survey
from eave.core.lib.event_helpers import get_internal_activity
from eave.core.lib.eventbrite import EventbriteUtility
from eave.core.lib.google_places import GooglePlacesUtility
from eave.core.lib.time_category import is_early_evening, is_early_morning, is_late_evening, is_late_morning
from eave.core.orm.activity_category import ActivityCategoryOrm
from eave.core.orm.eventbrite_event import EventbriteEventOrm
from eave.core.orm.evergreen_activity import EvergreenActivityOrm
from eave.core.orm.restaurant_category import MAGIC_BAR_RESTAURANT_CATEGORY_ID, RestaurantCategoryOrm
from eave.core.orm.search_region import SearchRegionOrm
from eave.core.orm.survey import SurveyOrm
from eave.core.shared.geo import Distance, GeoArea
from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.logging import LOGGER
from eave.stdlib.typing import JsonObject

_BREAKFAST_GOOGLE_RESTAURANT_CATEGORY_IDS = (
    "coffee_shop",
    "breakfast_restaurant",
    "bakery",
    "cafe",
)

_BRUNCH_GOOGLE_RESTAURANT_CATEGORY_IDS = (
    "brunch_restaurant",
    "breakfast_restaurant",
    "cafe",
)


@dataclass(kw_only=True)
class PlannerResult:
    cost_breakdown: CostBreakdown
    activity_plan: ActivityPlan | None
    reservation: Reservation | None


def _combine_restaurant_categories(individual_preferences: list[OutingPreferencesInput]) -> list[RestaurantCategoryOrm]:
    """
    Given a group of users, combine their restaurant category preferences
    into one list of preferences.

    The preferences that the users have in common will always be at the
    front of the list.
    """
    category_map: dict[UUID, int] = {}
    intersection: list[RestaurantCategoryOrm] = []
    difference: list[RestaurantCategoryOrm] = []

    # Create a map of category IDs with occurence counts.
    for preferences in individual_preferences:
        for category_id in preferences.restaurant_category_ids:
            # Exclude the special "Bar" category
            if category_id != MAGIC_BAR_RESTAURANT_CATEGORY_ID:
                category_map.setdefault(category_id, 0)
                category_map[category_id] += 1

    # Use the map of category ID occurence counts to find the common categories.
    for category_id, num_matches in category_map.items():
        category = RestaurantCategoryOrm.one_or_exception(restaurant_category_id=category_id)
        if num_matches == len(individual_preferences):
            intersection.append(category)
        else:
            difference.append(category)

    random.shuffle(intersection)
    random.shuffle(difference)
    result = intersection + difference

    if len(result) == 0:
        result = list(RestaurantCategoryOrm.defaults())  # Already a list, copying again for safety
        random.shuffle(result)

    return result


def _combine_activity_categories(individual_preferences: list[OutingPreferencesInput]) -> list[ActivityCategoryOrm]:
    """
    Given a group of users, combine their activity category preferences
    into one list of preferences.

    The preferences that the users have in common will always be at the
    front of the list.
    """
    category_map: dict[UUID, int] = {}
    intersection: list[ActivityCategoryOrm] = []
    difference: list[ActivityCategoryOrm] = []

    # Create a map of category / subcategory IDs with occurence counts.
    for preferences in individual_preferences:
        for category_id in preferences.activity_category_ids:
            category_map.setdefault(category_id, 0)
            category_map[category_id] += 1

    # Use the map of category / subcategory ID occurence counts to find the common categories.
    for category_id, num_matches in category_map.items():
        category = ActivityCategoryOrm.one_or_exception(activity_category_id=category_id)
        if num_matches == len(individual_preferences):
            intersection.append(category)
        else:
            difference.append(category)

    random.shuffle(intersection)
    random.shuffle(difference)

    result = intersection + difference

    if len(result) == 0:
        result = list(ActivityCategoryOrm.defaults())  # Already a list, copying again for safety
        random.shuffle(result)

    return result


def _combine_bar_openness(individual_preferences: list[OutingPreferencesInput]) -> bool:
    """
    Given a group of users, return False if any of the users is not open to
    going to a bar.
    """
    return all(
        MAGIC_BAR_RESTAURANT_CATEGORY_ID in preferences.restaurant_category_ids
        for preferences in individual_preferences
    )


class OutingPlanner:
    """
    Use this class to plan an outing for a group of users based on their outing
    constraints and personal preferences.

    Currently, an outing consists of food and a thing - eat at a well-rated
    restaurant, then go to an event or engage in a cute activity.
    """

    places: GooglePlacesUtility
    eventbrite: EventbriteUtility
    # maps: GoogleMapsUtility

    survey: SurveyOrm
    activity: Activity | None
    restaurant: Restaurant | None
    activity_start_time_local: datetime | None
    restaurant_arrival_time_local: datetime | None
    restaurant_departure_time_local: datetime | None

    group_restaurant_category_preferences: list[RestaurantCategoryOrm]
    group_activity_category_preferences: list[ActivityCategoryOrm]
    group_open_to_bars: bool

    excluded_eventbrite_event_ids: list[str]
    excluded_google_place_ids: list[str]
    excluded_evergreen_activity_ids: list[UUID]

    ctx: GraphQLContext

    def __init__(
        self,
        individual_preferences: list[OutingPreferencesInput],
        survey: SurveyOrm,
        ctx: GraphQLContext,
        activity: Activity | None = None,
        restaurant: Restaurant | None = None,
        activity_start_time: datetime | None = None,
        restaurant_arrival_time: datetime | None = None,
        excluded_eventbrite_event_ids: list[str] | None = None,
        excluded_google_place_ids: list[str] | None = None,
        excluded_evergreen_activity_ids: list[UUID] | None = None,
    ) -> None:
        self.places = GooglePlacesUtility()
        self.eventbrite = EventbriteUtility()

        self.survey = survey
        self.activity = activity
        self.restaurant = restaurant
        self.activity_start_time_local = (
            activity_start_time.astimezone(survey.timezone) if activity_start_time else None
        )
        self.restaurant_arrival_time_local = (
            restaurant_arrival_time.astimezone(survey.timezone) if restaurant_arrival_time else None
        )
        self.restaurant_departure_time_local = None

        self.group_restaurant_category_preferences = _combine_restaurant_categories(individual_preferences)
        self.group_activity_category_preferences = _combine_activity_categories(individual_preferences)
        self.group_open_to_bars = _combine_bar_openness(individual_preferences)

        self.excluded_google_place_ids = excluded_google_place_ids or []
        self.excluded_eventbrite_event_ids = excluded_eventbrite_event_ids or []
        self.excluded_evergreen_activity_ids = excluded_evergreen_activity_ids or []

        self.ctx = ctx

    async def plan_activity(self) -> Activity | None:
        """
        Plan an activity for the outing, taking into consideration the outing
        constraints and group preferences.

        For now, the activity always happens after a meal. We plan the activity
        first, then we find a restaurant nearby that users can eat at before
        the activity.
        """

        # The time+120 minutes is because the restaurant happens before the activity.
        start_time_local = self.survey.start_time_local + timedelta(minutes=120)
        self.activity_start_time_local = start_time_local
        end_time_local = start_time_local + timedelta(minutes=90)

        log_ctx = self._log_ctx()

        regions = [
            SearchRegionOrm.one_or_exception(search_region_id=search_area_id)
            for search_area_id in self.survey.search_area_ids
        ]

        if len(regions) == 0:
            # Failsafe - This should never happen
            LOGGER.warning("No activity search areas categories could be resolved; falling back to defaults", log_ctx)
            regions = list(SearchRegionOrm.all())  # already a list, doing this for safety

        random.shuffle(regions)

        within_areas = [region.area for region in regions]
        group_activity_category_preferences_ids = [cat.id for cat in self.group_activity_category_preferences]

        LOGGER.debug("searching for eventbrite events", log_ctx)

        # CASE 1: Recommend an Eventbrite event.
        async with eave.core.database.async_session.begin() as db_session:
            eventbrite_events_query = EventbriteEventOrm.select(
                start_time=start_time_local,
                budget=self.survey.budget,
                within_areas=within_areas,
                vivial_activity_category_ids=group_activity_category_preferences_ids,
                excluded_eventbrite_event_ids=self.excluded_eventbrite_event_ids,
            ).order_by(func.random())

            eventbrite_events_results = await db_session.scalars(eventbrite_events_query)

            for event_orm in eventbrite_events_results:
                try:
                    if activity := await self.eventbrite.get_eventbrite_activity(
                        event_id=event_orm.eventbrite_event_id,
                        survey=self.survey,
                    ):
                        self.activity = activity
                        return activity
                except Exception as e:
                    if SHARED_CONFIG.is_local:
                        raise
                    else:
                        LOGGER.exception(e)
                        continue

        LOGGER.debug("searching for evergreen activities", log_ctx)

        # CASE 2: Recommend an "evergreen" activity from our manually curated database.
        async with eave.core.database.async_session.begin() as db_session:
            evergreen_activities_query = EvergreenActivityOrm.select(
                within_areas=within_areas,
                activity_category_ids=group_activity_category_preferences_ids,
                open_at_local=start_time_local,
                budget=self.survey.budget,
                excluded_evergreen_activity_ids=self.excluded_evergreen_activity_ids,
            ).order_by(func.random())

            evergreen_activity_orms = await db_session.scalars(evergreen_activities_query)

        for evergreen_activity_orm in evergreen_activity_orms:
            if evergreen_activity := await get_internal_activity(
                event_id=str(evergreen_activity_orm.id), survey=self.survey
            ):
                self.activity = evergreen_activity
                return self.activity

        LOGGER.debug("searching for ice cream/bar fallback", log_ctx)

        # CASE 3: Recommend a bar or an ice cream shop as a fallback activity.
        is_evening = is_early_evening(self.survey.start_time_utc, self.survey.timezone) or is_late_evening(
            self.survey.start_time_utc, self.survey.timezone
        )

        # If it's night time, then send them to either an ice cream shop or a bar, depending on the group preferences.
        # Reminder that here we're recommending _activities_ not restaurants.
        place_type = "ice_cream_shop"
        if is_evening and self.group_open_to_bars:
            place_type = "bar"

        for search_area in within_areas:
            try:
                places_nearby = await self.places.get_places_nearby(
                    area=search_area,
                    included_primary_types=[place_type],
                )
            except Exception as e:
                if SHARED_CONFIG.is_local:
                    raise
                else:
                    LOGGER.exception(e)
                    continue

            if len(self.excluded_google_place_ids):
                places_nearby = [p for p in places_nearby if p.id not in self.excluded_google_place_ids]

            random.shuffle(places_nearby)

            for place in places_nearby:
                will_be_open = self.places.place_will_be_open(
                    place=place,
                    arrival_time=start_time_local,
                    departure_time=end_time_local,
                    timezone=self.survey.timezone,
                )

                # Select activities that are within (<=) their requested budget.
                if will_be_open and place.price_level <= self.survey.budget.google_places_price_level:
                    try:
                        self.activity = await self.places.activity_from_google_place(place=place)
                        return self.activity
                    except Exception as e:
                        if SHARED_CONFIG.is_local:
                            raise
                        else:
                            LOGGER.exception(e)
                            continue

        LOGGER.warning("no activity found", log_ctx)

        # CASE 4: No suitable activity was found :(
        self.activity = None
        return self.activity

    async def plan_restaurant(self) -> Restaurant | None:
        """
        Plan a restaurant for the outing, taking into consideration the outing
        activity, outing constraints and group preferences.

        For now, the meal always happens before the activity.
        """
        arrival_time_local = self.survey.start_time_local
        self.restaurant_arrival_time_local = arrival_time_local
        departure_time_local = arrival_time_local + timedelta(minutes=90)
        self.restaurant_departure_time_local = departure_time_local

        log_ctx = self._log_ctx()

        google_category_id_groups: list[list[str]] = []

        # If this is a morning outing, override user restaurant preferences and show them breakfast / brunch spots.
        if is_early_morning(arrival_time_local, self.survey.timezone):
            google_category_id_groups = [list(_BREAKFAST_GOOGLE_RESTAURANT_CATEGORY_IDS)]
        elif is_late_morning(arrival_time_local, self.survey.timezone):
            google_category_id_groups = [list(_BRUNCH_GOOGLE_RESTAURANT_CATEGORY_IDS)]
        else:
            # Already randomized in combiner funcs
            google_category_id_groups = [cat.google_category_ids for cat in self.group_restaurant_category_preferences]

        if len(google_category_id_groups) == 0:
            # Failsafe - This should never happen
            LOGGER.warning("No google category IDs could be resolved; falling back to defaults", log_ctx)

            # If included_primary_types is empty, this query returns everything, like car rental places and junk.
            # Although self.group_restaurant_category_preferences should never be empty, it's possible for there to be no google_category_ids here.
            # That should never happen, but if it does, we don't want to show bad results, so this is a failsafe.
            google_category_id_groups = [cat.google_category_ids for cat in RestaurantCategoryOrm.defaults()]
            random.shuffle(google_category_id_groups)

        # If an activity has been selected, try that search area first.
        if self.activity:
            within_areas = [
                GeoArea(
                    center=self.activity.venue.location.coordinates,
                    rad=Distance(miles=miles),
                )
                for miles in (5, 10, 15, 20)
            ]
        else:
            within_areas = [
                SearchRegionOrm.one_or_exception(search_region_id=search_area_id).area
                for search_area_id in self.survey.search_area_ids
            ]
            random.shuffle(within_areas)

        if len(within_areas) == 0:
            # Failsafe - This should never happen
            LOGGER.warning("No restaurant search areas categories could be resolved; falling back to defaults", log_ctx)
            # If there are no search areas given (which shouldn't happen but technically could), fallback to all of them.
            within_areas = [s.area for s in SearchRegionOrm.all()]
            random.shuffle(within_areas)

        LOGGER.debug("finding restaurant", log_ctx)

        # Find a restaurant that meets the outing constraints.
        for area in within_areas:
            for google_category_id_group in google_category_id_groups:
                try:
                    restaurants_nearby = await self.places.get_places_nearby(
                        area=area,
                        included_primary_types=google_category_id_group,
                    )
                except Exception as e:
                    if SHARED_CONFIG.is_local:
                        raise
                    else:
                        LOGGER.exception(e)
                        continue

                if len(self.excluded_google_place_ids):
                    restaurants_nearby = [r for r in restaurants_nearby if r.id not in self.excluded_google_place_ids]

                if len(restaurants_nearby) == 0:
                    # Call `continue` because there is no need to continue if everything was filtered out.
                    # That's a confusing sentence.
                    LOGGER.warning(
                        "no restaurants found for google category ids",
                        log_ctx,
                        {"google_category_ids": google_category_id_group},
                    )
                    continue

                random.shuffle(restaurants_nearby)

                perform_lte_price_level_comparison = arrival_time_local.hour < 11
                if perform_lte_price_level_comparison:
                    # Before 11am, most restaurants are cheaper ($$ or less).
                    # So if someone chooses $$$-$$$$, we would rarely should them a restaurant recommendation.
                    # So in this case, we sort the (already shuffled) retrieved restaurants by price level descending.
                    # We don't do this for >= 11am because we don't want to recommend McDonald's for an expensive night out.
                    restaurants_nearby.sort(key=lambda place: place.price_level.value, reverse=True)  # in-place sort

                for restaurant in restaurants_nearby:
                    if perform_lte_price_level_comparison:
                        # <=
                        # If we're < 11am, then find restaurants that have price less <= the selected price level
                        price_level_matches = restaurant.price_level <= self.survey.budget.google_places_price_level
                    else:
                        # ==
                        # Otherwise, find only restaurants that match the selected price livel
                        price_level_matches = restaurant.price_level == self.survey.budget.google_places_price_level

                    will_be_open = self.places.place_will_be_open(
                        place=restaurant,
                        arrival_time=arrival_time_local,
                        departure_time=departure_time_local,
                        timezone=self.survey.timezone,
                    )

                    # Select restaurants that _match_ their requested budget.
                    # So if they request an expensive date, we don't recommend McDonald's.
                    if will_be_open and price_level_matches:
                        try:
                            self.restaurant = await self.places.restaurant_from_google_place(place=restaurant)
                            return self.restaurant
                        except Exception as e:
                            if SHARED_CONFIG.is_local:
                                raise
                            else:
                                LOGGER.exception(e)
                                continue

        LOGGER.warning("no restaurant found", log_ctx)

        # No restaurant was found :(
        self.restaurant = None
        return self.restaurant

    async def plan(self) -> PlannerResult:
        """
        Plan an outing for a group of users, taking into consideration outing
        constraints and group preferences.
        """
        await self.plan_activity()
        await self.plan_restaurant()

        total_cost_breakdown = CostBreakdown()

        if self.activity and self.activity_start_time_local:
            activity_plan = ActivityPlan(
                activity=self.activity,
                start_time=self.activity_start_time_local,
                headcount=self.survey.headcount,
            )

            total_cost_breakdown += activity_plan.calculate_cost_breakdown()
        else:
            activity_plan = None

        if self.restaurant and self.restaurant_arrival_time_local:
            reservation = Reservation(
                restaurant=self.restaurant,
                arrival_time=self.restaurant_arrival_time_local,
                headcount=self.survey.headcount,
            )

            total_cost_breakdown += reservation.calculate_cost_breakdown()
        else:
            reservation = None

        return PlannerResult(
            cost_breakdown=total_cost_breakdown,
            activity_plan=activity_plan,
            reservation=reservation,
        )

    def _log_ctx(self) -> LogContext:
        ctx = log_ctx(self.ctx)

        planner_ctx = {
            "group_activity_category_preferences": [p.name for p in self.group_activity_category_preferences],
            "search_areas": [
                SearchRegionOrm.one_or_exception(search_region_id=search_area_id).name
                for search_area_id in self.survey.search_area_ids
            ],
            "survey": dataclasses.asdict(Survey.from_orm(self.survey)),
            "start_time_local": self.activity_start_time_local.isoformat() if self.activity_start_time_local else None,
            "restaurant_arrival_time_local": self.restaurant_arrival_time_local.isoformat()
            if self.restaurant_arrival_time_local
            else None,
            "excluded_eventbrite_event_ids": self.excluded_eventbrite_event_ids,
            "excluded_google_place_ids": self.excluded_google_place_ids,
            "excluded_evergreen_activity_ids": [x.hex for x in self.excluded_evergreen_activity_ids],
        }

        extra = ctx.setdefault("extra", {})
        extra["planner"] = planner_ctx

        return ctx
