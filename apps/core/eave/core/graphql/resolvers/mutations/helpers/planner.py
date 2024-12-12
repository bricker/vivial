import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import UUID

from google.maps.places_v1 import PlacesAsyncClient
from sqlalchemy import func

import eave.core.database
from eave.core.config import CORE_API_APP_CONFIG
from eave.core.graphql.types.activity import Activity
from eave.core.graphql.types.outing import OutingPreferencesInput
from eave.core.graphql.types.restaurant import Restaurant
from eave.core.lib.eventbrite import activity_from_eventbrite_event
from eave.core.lib.google_places import (
    activity_from_google_place,
    get_places_nearby,
    place_is_in_budget,
    place_will_be_open,
    restaurant_from_google_place,
)
from eave.core.lib.time_category import is_early_evening, is_early_morning, is_late_evening, is_late_morning
from eave.core.orm.activity_category import ActivityCategoryOrm
from eave.core.orm.eventbrite_event import EventbriteEventOrm
from eave.core.orm.restaurant_category import MAGIC_BAR_RESTAURANT_CATEGORY_ID, RestaurantCategoryOrm
from eave.core.orm.search_region import SearchRegionOrm
from eave.core.orm.survey import SurveyOrm
from eave.core.shared.geo import Distance, GeoArea, GeoPoint
from eave.stdlib.eventbrite.client import EventbriteClient, GetEventQuery
from eave.stdlib.eventbrite.models.expansions import Expansion
from eave.stdlib.logging import LOGGER

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
    activity: Activity | None
    activity_start_time: datetime | None
    restaurant: Restaurant | None
    restaurant_arrival_time: datetime | None
    driving_time: str | None


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
    return intersection + difference


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
    return intersection + difference


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

    places_client: PlacesAsyncClient
    eventbrite_client: EventbriteClient
    survey: SurveyOrm
    activity: Activity | None
    restaurant: Restaurant | None
    activity_start_time_local: datetime | None
    restaurant_arrival_time_local: datetime | None

    group_restaurant_category_preferences: list[RestaurantCategoryOrm]
    group_activity_category_preferences: list[ActivityCategoryOrm]
    group_open_to_bars: bool

    def __init__(
        self,
        individual_preferences: list[OutingPreferencesInput],
        survey: SurveyOrm,
        activity: Activity | None = None,
        restaurant: Restaurant | None = None,
        activity_start_time: datetime | None = None,
        restaurant_arrival_time: datetime | None = None,
    ) -> None:
        self.places_client = PlacesAsyncClient()
        self.eventbrite_client = EventbriteClient(api_key=CORE_API_APP_CONFIG.eventbrite_api_key)
        self.survey = survey
        self.activity = activity
        self.restaurant = restaurant
        self.activity_start_time_local = (
            activity_start_time.astimezone(survey.timezone) if activity_start_time else None
        )
        self.restaurant_arrival_time_local = (
            restaurant_arrival_time.astimezone(survey.timezone) if restaurant_arrival_time else None
        )

        self.group_restaurant_category_preferences = _combine_restaurant_categories(individual_preferences)
        self.group_activity_category_preferences = _combine_activity_categories(individual_preferences)
        self.group_open_to_bars = _combine_bar_openness(individual_preferences)

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
        random.shuffle(self.survey.search_area_ids)

        within_areas = [
            SearchRegionOrm.one_or_exception(search_region_id=search_area_id).area
            for search_area_id in self.survey.search_area_ids
        ]

        # CASE 1: Recommend an Eventbrite event.
        query = EventbriteEventOrm.select(
            time_range_contains=start_time_local,
            cost_range_contains=self.survey.budget.upper_limit_cents,
            within_areas=within_areas,
            vivial_activity_category_ids=[cat.id for cat in self.group_activity_category_preferences],
        ).order_by(func.random())

        async with eave.core.database.async_session.begin() as db_session:
            results = await db_session.scalars(query)

            for event_orm in results:
                try:
                    eventbrite_event = await self.eventbrite_client.get_event_by_id(
                        event_id=event_orm.eventbrite_event_id,
                        query=GetEventQuery(
                            expand=Expansion.all(),
                        ),
                    )
                    self.activity = await activity_from_eventbrite_event(self.eventbrite_client, event=eventbrite_event)
                    return self.activity
                except Exception as e:
                    LOGGER.exception(e)
                    continue

        # CASE 2: Recommend an "evergreen" activity from our manually curated database.
        # for search_area_id in self.constraints.search_area_ids:
        #     for category in self.preferences.activity_categories:
        #         activities = []
        # TODO: Fetch from internal database when that is ready (pending Bryan).
        # activities = get_evergreen_activities(
        #     search_area_id=search_area_id,
        #     category_id=category.id,
        #     subcategory_id=category.subcategory_id,
        #     start_time=activity_start_time,
        #     end_time=activity_end_time,
        #     budget=ACTIVITY_BUDGET_MAP[self.constraints.budget],
        # )
        # if len(activities):
        #     random.shuffle(activities)
        #     geo_location = GeoLocation(TODO)
        #     self.activity = OutingComponent(TODO)
        #     return self.activity

        # CASE 3: Recommend a bar or an ice cream shop as a fallback activity.
        is_evening = is_early_evening(self.survey.start_time_utc, self.survey.timezone) or is_late_evening(
            self.survey.start_time_utc, self.survey.timezone
        )

        # If it's night time, then send them to either an ice cream shop or a bar, depending on the group preferences.
        # Reminder that here we're recommending _activities_ not restaurants.
        place_type = "ice_cream_shop"
        if is_evening and self.group_open_to_bars:
            place_type = "bar"

        for search_area_id in self.survey.search_area_ids:
            region = SearchRegionOrm.one_or_exception(search_region_id=search_area_id)

            places_nearby = await get_places_nearby(
                places_client=self.places_client,
                area=region.area,
                included_primary_types=[place_type],
            )

            random.shuffle(places_nearby)

            for place in places_nearby:
                will_be_open = place_will_be_open(
                    place=place,
                    arrival_time=start_time_local,
                    departure_time=end_time_local,
                    timezone=self.survey.timezone,
                )
                is_in_budget = place_is_in_budget(place, self.survey.budget)

                if will_be_open and is_in_budget:
                    self.activity = await activity_from_google_place(self.places_client, place=place)
                    return self.activity

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
        search_areas = []

        # If this is a morning outing, override user restaurant preferences and show them breakfast / brunch spots.
        if is_early_morning(arrival_time_local, self.survey.timezone):
            google_category_ids = list(_BREAKFAST_GOOGLE_RESTAURANT_CATEGORY_IDS)
            random.shuffle(google_category_ids)
        elif is_late_morning(arrival_time_local, self.survey.timezone):
            google_category_ids = list(_BRUNCH_GOOGLE_RESTAURANT_CATEGORY_IDS)
            random.shuffle(google_category_ids)
        else:
            # Already randomized in combiner funcs
            google_category_ids = [
                gcid for cat in self.group_restaurant_category_preferences for gcid in cat.google_category_ids
            ]

        # If an activity has been selected, use that as the search area.
        if self.activity:
            search_areas = [
                GeoArea(
                    center=self.activity.venue.location.coordinates,
                    rad=Distance(miles=5),
                ),
            ]

        # TODO: Sort areas by distance to the activity location.
        for search_area_id in self.survey.search_area_ids:
            search_areas.append(SearchRegionOrm.one_or_exception(search_region_id=search_area_id).area)

        # Find a restaurant that meets the outing constraints.
        for area in search_areas:
            restaurants_nearby = await get_places_nearby(
                places_client=self.places_client,
                area=area,
                included_primary_types=google_category_ids,
            )

            random.shuffle(restaurants_nearby)

            for restaurant in restaurants_nearby:
                will_be_open = place_will_be_open(
                    place=restaurant,
                    arrival_time=arrival_time_local,
                    departure_time=departure_time_local,
                    timezone=self.survey.timezone,
                )
                is_in_budget = place_is_in_budget(restaurant, self.survey.budget)

                if will_be_open and is_in_budget:
                    self.restaurant = await restaurant_from_google_place(self.places_client, place=restaurant)
                    return self.restaurant

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
        return PlannerResult(
            activity=self.activity,
            activity_start_time=self.activity_start_time_local,
            restaurant=self.restaurant,
            restaurant_arrival_time=self.restaurant_arrival_time_local,
            driving_time=None,
        )
