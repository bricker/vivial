from datetime import timedelta
import random
import os

from eave.stdlib.eventbrite.client import EventbriteClient
from eave.stdlib.google.places.client import GooglePlacesClient

from eave.stdlib.eventbrite.models.event import Event, EventStatus
from eave.stdlib.google.places.models.place import Place
from models.geo_area import GeoArea
from models.outing import OutingConstraints, OutingPlan, OutingSource, OutingComponent
from models.user import UserPreferences, User
from models.category import Category

from constants.restaurants import RESTAURANT_FIELD_MASK, BREAKFAST_RESTAURANT_CATEGORIES, BRUNCH_RESTAURANT_CATEGORIES
from constants.activities import ACTIVITY_BUDGET_MAP
from constants.areas import LOS_ANGELES_AREA_MAP

from helpers.place import place_will_be_open, place_is_in_budget, place_is_accessible
from helpers.time import is_early_morning, is_late_morning, is_early_evening, is_late_evening

# TODO: Convert internal restaurant category mappings to Google Places category mappings (pending Bryan).
# TODO: Convert internal event category mappings to Eventbrite category mappings (pending Bryan).
class Outing:
    places = GooglePlacesClient(api_key=os.environ["GOOGLE_PLACES_API_KEY"])
    eventbrite = EventbriteClient(api_key=os.environ["EVENTBRITE_API_KEY"])
    preferences: UserPreferences
    constraints: OutingConstraints
    activity: OutingComponent | None
    restaurant: OutingComponent | None


    def __init__(self, group: list[User], constraints: OutingConstraints, activity: OutingComponent | None = None, restaurant: OutingComponent | None = None) -> None:
        self.preferences = self.__combine_preferences(group)
        self.constraints = constraints
        self.activity = activity
        self.restaurant = restaurant


    def __combine_restaurant_categories(self, group: list[User]) -> list[Category]:
        category_map = {}
        intersection = []
        difference = []

        for user in group:
            for category in user.preferences.restaurant_categories:
                if category.id not in category_map:
                    category_map[category.id] = 0
                category_map[category.id] += 1

        for category_id in category_map:
            if category_map[category_id] == len(group):
                intersection.append(Category(id=category_id))
            else:
                difference.append(Category(id=category_id))

        random.shuffle(intersection)
        random.shuffle(difference)
        return intersection + difference


    def __combine_activity_categories(self, group: list[User]) -> list[Category]:
        category_map = {}
        intersection = []
        difference = []

        for user in group:
            for category in user.preferences.activity_categories:
                if category.id not in category_map:
                    category_map[category.id] = {}
                if category.subcategory_id not in category_map[category.id]:
                    category_map[category.id][category.subcategory_id] = 0
                category_map[category.id][category.subcategory_id] += 1

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
            for user in group:
                if user.preferences.requires_wheelchair_accessibility:
                    return True
            return False


    def __combine_bar_openness(self, group: list[User]) -> bool:
        for user in group:
            if not user.preferences.open_to_bars:
                return False
        return True


    def __combine_preferences(self, group: list[User]) -> UserPreferences:
        return UserPreferences(
            restaurant_categories = self.__combine_restaurant_categories(group),
            activity_categories = self.__combine_activity_categories(group),
            requires_wheelchair_accessibility = self.__combine_wheelchair_needs(group),
            open_to_bars = self.__combine_bar_openness(group),
        )


    async def plan_activity(self) -> OutingComponent | None:
        activity_start_time = self.constraints.start_time + timedelta(minutes=120)
        activity_end_time = activity_start_time + timedelta(minutes=90)
        random.shuffle(self.constraints.search_area_ids)

        # CASE 1: Recommend and Eventbrite event.
        for search_area_id in self.constraints.search_area_ids:
            for category in self.preferences.activity_categories:
                events = []
                # TODO: Fetch from internal database when that is ready (pending Bryan).
                # TODO: Pass in expansions: venue,ticket_availability (pending Bryan)
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
                                    self.activity = OutingComponent(OutingSource.EVENTBRITE, event_details)
                                    return self.activity

        # CASE 2: Recommend an "evergreen" activity from our manually curated database.
        for search_area_id in self.constraints.search_area_ids:
            for category in self.preferences.activity_categories:
                activities = []
                # TODO: Fetch from internal database when that is ready (pending Bryan).
                # activities = get_evergreen_activities(
                #     search_area_id=search_area_id,
                #     category_id=category.id,
                #     subcategory_id=category.subcategory_id,
                #     start_time=activity_start_time,
                #     end_time=activity_end_time,
                #     budget=ACTIVITY_BUDGET_MAP[self.constraints.budget],
                # )
                if len(activities):
                    self.activity = OutingComponent(OutingSource.INTERNAL, random.choice(activities))
                    return self.activity

        # CASE 3: Recommend a bar or an ice cream shop as a fallback activity.
        place_type = "ice_cream_shop"
        if (is_early_evening(activity_start_time) or is_late_evening(activity_start_time)) and self.preferences.open_to_bars:
            place_type = "bar"

        for search_area_id in self.constraints.search_area_ids:
            area = LOS_ANGELES_AREA_MAP[search_area_id]
            if places_nearby := await self.places.search_nearby(
                field_mask=RESTAURANT_FIELD_MASK,
                latitude=area.lat,
                longitude=area.lon,
                radius=area.rad.meters,
                included_primary_types=[place_type]
            ):
                random.shuffle(places_nearby)
                for place in places_nearby:
                    will_be_open = place_will_be_open(place, activity_start_time, activity_end_time)
                    is_in_budget = place_is_in_budget(place, self.constraints.budget)
                    is_accessible = place_is_accessible(place, self.preferences.requires_wheelchair_accessibility)
                    if will_be_open and is_in_budget and is_accessible:
                        self.activity = OutingComponent(OutingSource.GOOGLE, place)
                        return self.activity

        # CASE 4: No suitable activity was found :(
        self.activity = None
        return self.activity


    async def plan_restaurant(self) -> OutingComponent | None:
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
        if self.activity:
            location = None
            if self.activity.source == OutingSource.GOOGLE:
                location = self.activity.details.get("location")
            elif self.activity.source == OutingSource.EVENTBRITE:
                location = self.activity.details.get("venue")

            if location:
                lat = location.get("latitude")
                lon = location.get("longitude")
                if lat and lon:
                    search_areas = [GeoArea(lat=lat, lon=lon, rad_miles=5)]

        # Otherwise, use the search areas specified in the date constraints.
        else:
            for search_area_id in self.constraints.search_area_ids:
                search_areas.append(LOS_ANGELES_AREA_MAP[search_area_id])
            random.shuffle(search_areas)

        # Find a restaurant that meets the outing constraints.
        for area in search_areas:
            for category in restaurant_categories:
                if restaurants_nearby := await self.places.search_nearby(
                    field_mask=RESTAURANT_FIELD_MASK,
                    latitude=area.lat,
                    longitude=area.lon,
                    radius=area.rad.meters,
                    included_primary_types=[category.id]
                ):
                    random.shuffle(restaurants_nearby)
                    for restaurant in restaurants_nearby:
                        will_be_open = place_will_be_open(restaurant, arrival_time, departure_time)
                        is_in_budget = place_is_in_budget(restaurant, self.constraints.budget)
                        is_accessible = place_is_accessible(restaurant, self.preferences.requires_wheelchair_accessibility)
                        if will_be_open and is_in_budget and is_accessible:
                            self.restaurant = OutingComponent(OutingSource.GOOGLE, restaurant)
                            return self.restaurant

        # No restaurant was found :(
        self.restaurant = None
        return self.restaurant


    async def plan(self) -> OutingPlan:
        await self.plan_activity()
        await self.plan_restaurant()
        return OutingPlan(self.activity, self.restaurant)
