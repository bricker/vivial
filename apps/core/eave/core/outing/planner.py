import random
from datetime import timedelta
from uuid import UUID

from google.maps import places_v1
from sqlalchemy import func

import eave.core.internal.database
from eave.core.internal.config import CORE_API_APP_CONFIG
from eave.core.internal.orm.eventbrite_event import EventbriteEventOrm
from eave.core.lib.geo import Distance, GeoArea, GeoPoint
from eave.core.outing.constants.activities import ACTIVITY_BUDGET_MAP_CENTS, get_vivial_subcategory_by_id
from eave.stdlib.eventbrite.client import EventbriteClient
from eave.stdlib.eventbrite.models.event import EventStatus
from eave.stdlib.logging import LOGGER

from .constants.areas import ALL_AREAS
from .constants.restaurants import (
    BREAKFAST_RESTAURANT_CATEGORIES,
    BRUNCH_RESTAURANT_CATEGORIES,
    RESTAURANT_FIELD_MASK,
    get_vivial_restaurant_category_by_id,
)
from .helpers.place import get_places_nearby, place_is_accessible, place_is_in_budget, place_will_be_open
from .helpers.time import is_early_evening, is_early_morning, is_late_evening, is_late_morning
from .models.category import ActivitySubcategory, RestaurantCategory
from .models.outing import OutingComponent, OutingConstraints, OutingPlan
from .models.sources import ActivitySource, RestaurantSource
from .models.user import User, UserPreferences


# TODO: Convert internal restaurant category mappings to Google Places category mappings (pending Bryan).
# TODO: Convert internal event category mappings to Eventbrite category mappings (pending Bryan).
class OutingPlanner:
    """
    Use this class to plan an outing for a group of users based on their outing
    constraints and personal preferences.

    Currently, an outing consists of food and a thing - eat at a well-rated
    restaurant, then go to an event or engage in a cute activity.
    """

    places: places_v1.PlacesClient
    eventbrite: EventbriteClient
    preferences: UserPreferences
    constraints: OutingConstraints
    activity: OutingComponent | None
    restaurant: OutingComponent | None

    def __init__(
        self,
        group: list[User],
        constraints: OutingConstraints,
        activity: OutingComponent | None = None,
        restaurant: OutingComponent | None = None,
    ) -> None:
        self.places = places_v1.PlacesClient()
        self.eventbrite = EventbriteClient(api_key=CORE_API_APP_CONFIG.eventbrite_api_key)
        self.preferences = self._combine_preferences(group)
        self.constraints = constraints
        self.activity = activity
        self.restaurant = restaurant

    def _combine_restaurant_categories(self, group: list[User]) -> list[RestaurantCategory]:
        """
        Given a group of users, combine their restaurant category preferences
        into one list of preferences.

        The preferences that the users have in common will always be at the
        front of the list.
        """
        category_map: dict[UUID, int] = {}
        intersection: list[RestaurantCategory] = []
        difference: list[RestaurantCategory] = []

        # Create a map of category IDs with occurance counts.
        for user in group:
            for category in user.preferences.restaurant_categories:
                category_map.setdefault(category.id, 0)
                category_map[category.id] += 1

        # Use the map of category ID occurance counts to find the common categories.
        for category_id, num_matches in category_map.items():
            category = get_vivial_restaurant_category_by_id(category_id)
            if num_matches == len(group):
                intersection.append(category)
            else:
                difference.append(category)

        random.shuffle(intersection)
        random.shuffle(difference)
        return intersection + difference

    def _combine_activity_categories(self, group: list[User]) -> list[ActivitySubcategory]:
        """
        Given a group of users, combine their activity category preferences
        into one list of preferences.

        The preferences that the users have in common will always be at the
        front of the list.
        """
        category_map: dict[UUID, int] = {}
        intersection: list[ActivitySubcategory] = []
        difference: list[ActivitySubcategory] = []

        # Create a map of category / subcategory IDs with occurence counts.
        for user in group:
            for category in user.preferences.activity_categories:
                category_map.setdefault(category.id, 0)
                category_map[category.id] += 1

        # Use the map of category / subcategory ID occurence counts to find the common categories.
        for category_id, num_matches in category_map.items():
            category = get_vivial_subcategory_by_id(category_id)
            if num_matches == len(group):
                intersection.append(category)
            else:
                difference.append(category)

        random.shuffle(intersection)
        random.shuffle(difference)
        return intersection + difference

    def _combine_wheelchair_needs(self, group: list[User]) -> bool:
        """
        Given a group of users, return True if any of the users requires
        wheelchair accessibility.
        """
        return any(user.preferences.requires_wheelchair_accessibility for user in group)

    def _combine_bar_openness(self, group: list[User]) -> bool:
        """
        Given a group of users, return False if any of the users is not open to
        going to a bar.
        """
        return all(user.preferences.open_to_bars for user in group)

    def _combine_preferences(self, group: list[User]) -> UserPreferences:
        """
        Given a group of users, combine their outing preferences. The logic
        throughout this class gives priority to common preferences.
        """
        return UserPreferences(
            restaurant_categories=self._combine_restaurant_categories(group),
            activity_categories=self._combine_activity_categories(group),
            requires_wheelchair_accessibility=self._combine_wheelchair_needs(group),
            open_to_bars=self._combine_bar_openness(group),
        )

    async def plan_activity(self) -> OutingComponent | None:
        """
        Plan an activity for the outing, taking into consideration the outing
        constraints and group preferences.

        For now, the activity always happens after a meal. We plan the activity
        first, then we find a restaurant nearby that users can eat at before
        the activity.
        """
        activity_start_time = self.constraints.start_time + timedelta(minutes=120)
        activity_end_time = activity_start_time + timedelta(minutes=90)
        random.shuffle(self.constraints.search_area_ids)

        # CASE 1: Recommend an Eventbrite event.
        query = EventbriteEventOrm.select(
            time_range_contains=activity_start_time,
            cost_range_contains=ACTIVITY_BUDGET_MAP_CENTS[self.constraints.budget],
            within_areas=[ALL_AREAS[search_area_id].area for search_area_id in self.constraints.search_area_ids],
            subcategory_ids=[cat.id for cat in self.preferences.activity_categories],
        ).order_by(func.random())

        async with eave.core.internal.database.async_session.begin() as db_session:
            results = await db_session.scalars(query)

            for event in results:
                try:
                    event_details = await self.eventbrite.get_event_by_id(event_id=event.eventbrite_event_id)

                    if not (ticket_availability := event_details.get("ticket_availability")):
                        LOGGER.warning(
                            "Missing ticket_availability; excluding event.",
                            {"eventbrite_event_id": event.eventbrite_event_id},
                        )
                        continue

                    if not ticket_availability.get("has_available_tickets"):
                        LOGGER.warning(
                            "has_available_tickets=False; excluding event.",
                            {"eventbrite_event_id": event.eventbrite_event_id},
                        )
                        continue

                    if event_details.get("status") != EventStatus.LIVE:
                        LOGGER.warning(
                            "status != live; excluding event.", {"eventbrite_event_id": event.eventbrite_event_id}
                        )
                        continue

                    if not (venue := event_details.get("venue")):
                        LOGGER.warning(
                            "Missing venue; excluding event.", {"eventbrite_event_id": event.eventbrite_event_id}
                        )
                        continue

                    if (lat := venue.get("latitude")) is None:
                        LOGGER.warning(
                            "Missing latitude; excluding event.", {"eventbrite_event_id": event.eventbrite_event_id}
                        )
                        continue

                    if (lon := venue.get("longitude")) is None:
                        LOGGER.warning(
                            "Missing longitude; excluding event.", {"eventbrite_event_id": event.eventbrite_event_id}
                        )
                        continue

                    description = await self.eventbrite.get_event_description(event_id=event.eventbrite_event_id)
                    event_details["description"] = description

                    self.activity = OutingComponent(
                        source=ActivitySource.EVENTBRITE,
                        event=event_details,
                        location=GeoPoint(lat=float(lat), lon=float(lon)),
                    )
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
        is_evening = is_early_evening(activity_start_time) or is_late_evening(activity_start_time)
        place_type = "ice_cream_shop"
        if is_evening and self.preferences.open_to_bars:
            place_type = "bar"

        for search_area_id in self.constraints.search_area_ids:
            region = ALL_AREAS[search_area_id]
            places_nearby = get_places_nearby(
                client=self.places,
                latitude=region.area.center.lat,
                longitude=region.area.center.lon,
                radius_meters=region.area.rad.meters,
                included_primary_types=[place_type],
                field_mask=RESTAURANT_FIELD_MASK,
            )
            random.shuffle(places_nearby)
            for place in places_nearby:
                if self.preferences.requires_wheelchair_accessibility and not place_is_accessible(place):
                    continue
                will_be_open = place_will_be_open(place, activity_start_time, activity_end_time)
                is_in_budget = place_is_in_budget(place, self.constraints.budget)
                if will_be_open and is_in_budget and place.location:
                    lat = place.location.latitude
                    lon = place.location.longitude
                    if lat and lon:
                        self.activity = OutingComponent(
                            source=RestaurantSource.GOOGLE_PLACES, place=place, location=GeoPoint(lat=lat, lon=lon)
                        )
                        return self.activity

        # CASE 4: No suitable activity was found :(
        self.activity = None
        return self.activity

    async def plan_restaurant(self) -> OutingComponent | None:
        """
        Plan a restaurant for the outing, taking into consideration the outing
        activity, outing constraints and group preferences.

        For now, the meal always happens before the activity.
        """
        arrival_time = self.constraints.start_time
        departure_time = arrival_time + timedelta(minutes=90)
        restaurant_categories = self.preferences.restaurant_categories
        search_areas = []

        # If this is a morning outing, override user restaurant preferences and show them breakfast / brunch spots.
        if is_early_morning(self.constraints.start_time):
            restaurant_categories = BREAKFAST_RESTAURANT_CATEGORIES.copy()
            random.shuffle(restaurant_categories)
        elif is_late_morning(self.constraints.start_time):
            restaurant_categories = BRUNCH_RESTAURANT_CATEGORIES.copy()
            random.shuffle(restaurant_categories)

        # If an activity has been selected, use that as the search area.
        if self.activity and self.activity.location:
            search_areas = [
                GeoArea(
                    center=GeoPoint(lat=self.activity.location.lat, lon=self.activity.location.lon),
                    rad=Distance(miles=5),
                ),
            ]

        # TODO: Sort areas by distance to the activity location.
        for search_area_id in self.constraints.search_area_ids:
            search_areas.append(ALL_AREAS[search_area_id].area)

        # Find a restaurant that meets the outing constraints.
        for area in search_areas:
            for category in restaurant_categories:
                restaurants_nearby = get_places_nearby(
                    client=self.places,
                    latitude=area.center.lat,
                    longitude=area.center.lon,
                    radius_meters=area.rad.meters,
                    included_primary_types=category.google_category_ids,  # FIXME: This will send all of the google category IDs associated with a single Vivial restaurant category. So if a restaurant is "Brunch" and "Vietnamese", then the results could return just Vietnamese restaurants.
                    field_mask=RESTAURANT_FIELD_MASK,
                )
                random.shuffle(restaurants_nearby)
                for restaurant in restaurants_nearby:
                    if self.preferences.requires_wheelchair_accessibility and not place_is_accessible(restaurant):
                        continue
                    will_be_open = place_will_be_open(restaurant, arrival_time, departure_time)
                    is_in_budget = place_is_in_budget(restaurant, self.constraints.budget)
                    if will_be_open and is_in_budget:
                        if restaurant.location:
                            lat = restaurant.location.latitude
                            lon = restaurant.location.longitude
                            if lat and lon:
                                self.restaurant = OutingComponent(
                                    source=RestaurantSource.GOOGLE_PLACES,
                                    place=restaurant,
                                    location=GeoPoint(lat=lat, lon=lon),
                                )
                                return self.restaurant

        # No restaurant was found :(
        self.restaurant = None
        return self.restaurant

    async def plan(self) -> OutingPlan:
        """
        Plan an outing for a group of users, taking into consideration outing
        constraints and group preferences.
        """
        await self.plan_activity()
        await self.plan_restaurant()
        return OutingPlan(self.activity, self.restaurant)
