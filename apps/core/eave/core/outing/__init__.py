import random
from datetime import timedelta

from eave.core.internal.config import CORE_API_APP_CONFIG
from eave.stdlib.eventbrite.client import EventbriteClient
from eave.stdlib.eventbrite.models.event import EventStatus
from eave.stdlib.google.places.client import GooglePlacesClient

from eave.core.internal.orm.eventbrite_event import EventbriteEventOrm
from eave.core.outing.constants.activities import ACTIVITY_BUDGET_MAP_CENTS

from .constants.areas import LOS_ANGELES_AREA_MAP
from .constants.restaurants import BREAKFAST_RESTAURANT_CATEGORIES, BRUNCH_RESTAURANT_CATEGORIES, RESTAURANT_FIELD_MASK
from .helpers.place import place_is_accessible, place_is_in_budget, place_will_be_open
from .helpers.time import is_early_evening, is_early_morning, is_late_evening, is_late_morning
from .models.category import Category
from .models.geo_area import GeoArea, GeoLocation
from .models.outing import OutingComponent, OutingConstraints, OutingPlan
from .models.sources import ActivitySource, RestaurantSource
from .models.user import User, UserPreferences

import eave.core.internal.database

# TODO: Convert internal restaurant category mappings to Google Places category mappings (pending Bryan).
# TODO: Convert internal event category mappings to Eventbrite category mappings (pending Bryan).
class Outing:
    """
    Use this class to plan an outing for a group of users based on their outing
    constraints and personal preferences.

    Currently, an outing consists of food and a thing - eat at a well-rated
    restaurant, then go to an event or engage in a cute activity.
    """

    places: GooglePlacesClient
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
        self.places = GooglePlacesClient(api_key=CORE_API_APP_CONFIG.google_places_api_key)
        self.eventbrite = EventbriteClient(api_key=CORE_API_APP_CONFIG.eventbrite_api_key)
        self.preferences = self.__combine_preferences(group)
        self.constraints = constraints
        self.activity = activity
        self.restaurant = restaurant

    def __combine_restaurant_categories(self, group: list[User]) -> list[Category]:
        """
        Given a group of users, combine their restaurant category preferences
        into one list of preferences.

        The preferences that the users have in common will always be at the
        front of the list.
        """
        category_map = {}
        intersection = []
        difference = []

        # Create a map of category IDs with occurance counts.
        for user in group:
            for category in user.preferences.restaurant_categories:
                if category.id not in category_map:
                    category_map[category.id] = 0
                category_map[category.id] += 1

        # Use the map of category ID occurance counts to find the common categories.
        for category_id in category_map:
            if category_map[category_id] == len(group):
                intersection.append(Category(id=category_id))
            else:
                difference.append(Category(id=category_id))

        random.shuffle(intersection)
        random.shuffle(difference)
        return intersection + difference

    def __combine_activity_categories(self, group: list[User]) -> list[Category]:
        """
        Given a group of users, combine their activity category preferences
        into one list of preferences.

        The preferences that the users have in common will always be at the
        front of the list.
        """
        category_map = {}
        intersection = []
        difference = []

        # Create a map of category / subcategory IDs with occurance counts.
        for user in group:
            for category in user.preferences.activity_categories:
                if category.id not in category_map:
                    category_map[category.id] = {}
                if category.subcategory_id not in category_map[category.id]:
                    category_map[category.id][category.subcategory_id] = 0
                category_map[category.id][category.subcategory_id] += 1

        # Use the map of category / subcategory ID occurance counts to find the common categories.
        for category_id in category_map:
            for subcategory_id in category_map[category_id]:
                if category_map[category_id][subcategory_id] == len(group):
                    intersection.append(Category(category_id, subcategory_id))
                else:
                    difference.append(Category(category_id, subcategory_id))

        random.shuffle(intersection)
        random.shuffle(difference)
        return intersection + difference

    def __combine_wheelchair_needs(self, group: list[User]) -> bool:
        """
        Given a group of users, return True if any of the users requires
        wheelchair accessibility.
        """
        return any(user.preferences.requires_wheelchair_accessibility for user in group)

    def __combine_bar_openness(self, group: list[User]) -> bool:
        """
        Given a group of users, return False if any of the users is not open to
        going to a bar.
        """
        for user in group:
            if not user.preferences.open_to_bars:
                return False
        return True

    def __combine_preferences(self, group: list[User]) -> UserPreferences:
        """
        Given a group of users, combine their outing preferences. The logic
        throughout this class gives priority to common preferences.
        """
        return UserPreferences(
            restaurant_categories=self.__combine_restaurant_categories(group),
            activity_categories=self.__combine_activity_categories(group),
            requires_wheelchair_accessibility=self.__combine_wheelchair_needs(group),
            open_to_bars=self.__combine_bar_openness(group),
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

        # CASE 1: Recommend and Eventbrite event.
        for search_area_id in self.constraints.search_area_ids:
            for category in self.preferences.activity_categories:
                async with eave.core.internal.database.async_session.begin() as db_session:
                    results = await EventbriteEventOrm.query(
                        db_session,
                        params=EventbriteEventOrm.QueryParams(
                            time_range_contains=activity_start_time,
                            cost_range_contains=ACTIVITY_BUDGET_MAP_CENTS[self.constraints.budget],
                            subcategory_id=category.subcategory_id,
                        ),
                    )
                # events = get_eventbrite_events(
                #     search_area_id=search_area_id,
                #     category_id=category.id,
                #     subcategory_id=category.subcategory_id,
                #     start_time=activity_start_time,
                #     budget=ACTIVITY_BUDGET_MAP[self.constraints.budget],
                # )
                random.shuffle(events)
                for event in events:
                    if event_details := await self.eventbrite.get_event_by_id(event_id=event["id"]):
                        if ticket_availability := event_details.get("ticket_availability"):
                            has_available_tickets = ticket_availability.get("has_available_tickets")
                            is_live = event_details.get("status") == EventStatus.live
                            if has_available_tickets and is_live:
                                if description := await self.eventbrite.get_event_description(event_id=event["id"]):
                                    event_details["description"] = description
                                if venue := event_details.get("venue"):
                                    lat = venue.get("latitude")
                                    lon = venue.get("longitude")
                                    if lat and lon:
                                        self.activity = OutingComponent(
                                            ActivitySource.EVENTBRITE, event_details, GeoLocation(lat, lon)
                                        )
                                        return self.activity

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
        #     self.activity = OutingComponent(ActivitySource.INTERNAL, activities[0], geo_location)
        #     return self.activity

        # CASE 3: Recommend a bar or an ice cream shop as a fallback activity.
        is_evening = is_early_evening(activity_start_time) or is_late_evening(activity_start_time)
        place_type = "ice_cream_shop"
        if is_evening and self.preferences.open_to_bars:
            place_type = "bar"

        for search_area_id in self.constraints.search_area_ids:
            area = LOS_ANGELES_AREA_MAP[search_area_id]
            if places_nearby := await self.places.search_nearby(
                field_mask=RESTAURANT_FIELD_MASK,
                latitude=area.lat,
                longitude=area.lon,
                radius=area.rad.meters,
                included_primary_types=[place_type],
            ):
                random.shuffle(places_nearby)
                for place in places_nearby:
                    if self.preferences.requires_wheelchair_accessibility and not place_is_accessible(place):
                        continue
                    will_be_open = place_will_be_open(place, activity_start_time, activity_end_time)
                    is_in_budget = place_is_in_budget(place, self.constraints.budget)
                    if will_be_open and is_in_budget:
                        if location := place.get("location"):
                            lat = location.get("latitude")
                            lon = location.get("longitude")
                            if lat and lon:
                                self.activity = OutingComponent(
                                    RestaurantSource.GOOGLE_PLACES, place, GeoLocation(lat, lon)
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
            restaurant_categories = BREAKFAST_RESTAURANT_CATEGORIES
            random.shuffle(restaurant_categories)
        elif is_late_morning(self.constraints.start_time):
            restaurant_categories = BRUNCH_RESTAURANT_CATEGORIES
            random.shuffle(restaurant_categories)

        # If an activity has been selected, use that as the search area.
        if self.activity and self.activity.location:
            search_areas = [GeoArea(lat=self.activity.location.lat, lon=self.activity.location.lon, rad_miles=5)]

        # TODO: Sort areas by distance to the activity location.
        for search_area_id in self.constraints.search_area_ids:
            search_areas.append(LOS_ANGELES_AREA_MAP[search_area_id])

        # Find a restaurant that meets the outing constraints.
        for area in search_areas:
            for category in restaurant_categories:
                if restaurants_nearby := await self.places.search_nearby(
                    field_mask=RESTAURANT_FIELD_MASK,
                    latitude=area.lat,
                    longitude=area.lon,
                    radius=area.rad.meters,
                    included_primary_types=[category.id],
                ):
                    random.shuffle(restaurants_nearby)
                    for restaurant in restaurants_nearby:
                        if self.preferences.requires_wheelchair_accessibility and not place_is_accessible(restaurant):
                            continue
                        will_be_open = place_will_be_open(restaurant, arrival_time, departure_time)
                        is_in_budget = place_is_in_budget(restaurant, self.constraints.budget)
                        if will_be_open and is_in_budget:
                            if location := restaurant.get("location"):
                                lat = location.get("latitude")
                                lon = location.get("longitude")
                                if lat and lon:
                                    self.restaurant = OutingComponent(
                                        RestaurantSource.GOOGLE_PLACES, restaurant, GeoLocation(lat, lon)
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
