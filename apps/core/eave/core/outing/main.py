from datetime import datetime, timedelta
import random
import asyncio
import os

from eave.stdlib.eventbrite.client import EventbriteClient
from eave.stdlib.google.places.client import GooglePlacesClient

from eave.stdlib.eventbrite.models.event import Event, EventStatus
from eave.stdlib.google.places.models.place import Place
from models.outing import OutingConstraints, OutingPlan
from models.user import UserPreferences, User
from models.category import Category

from constants.restaurants import RESTAURANT_BUDGET_MAP, RESTAURANT_FIELD_MASK, BREAKFAST_RESTAURANT_CATEGORIES, BRUNCH_RESTAURANT_CATEGORIES
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
    activity: Event | Place | None
    restaurant: Place | None


    def __init__(self, group: list[User], constraints: OutingConstraints, activity: Event | Place | None, restaurant: Restaurant | None) -> None:
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


    async def plan_activity(self) -> Event | Place | None:
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
                                    self.activity = Event(**event_details)
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
                # if len(activities) > 0:
                #     random.shuffle(activities)
                #     self.activity = Activity(activities[0]**)
                #     return self.activity

        # CASE 3: Recommend a bar as the activity if it's evening.
        is_evening = is_early_evening(activity_start_time) or is_late_evening(activity_start_time)
        if self.preferences.open_to_bars and is_evening:
            for search_area_id in self.constraints.search_area_ids:
                area = LOS_ANGELES_AREA_MAP[search_area_id]
                if bars_nearby := await self.places.search_nearby(
                    field_mask=RESTAURANT_FIELD_MASK,
                    latitude=area.lat,
                    longitude=area.lon,
                    radius=area.rad.meters,
                    included_primary_types=["bar"]
                ):
                    random.shuffle(bars_nearby)
                    for bar in bars_nearby:
                        will_be_open = place_will_be_open(bar, activity_start_time, activity_end_time)
                        is_in_budget = place_is_in_budget(bar, self.constraints.budget)
                        is_accessible = place_is_accessible(bar, self.preferences.requires_wheelchair_accessibility)
                        if will_be_open and is_in_budget and is_accessible:
                            self.activity = Place(**bar)
                            return self.activity

        # CASE 4: No suitable activity was found :(
        self.activity = None
        return self.activity





    async def plan_restaurant(self) -> Place | None:
        restaurant_categories = self.preferences.restaurant_categories
        search_areas = []

        # If this is a morning outing, override user restaurant preferences and show them breakfast / brunch spots.
        if is_early_morning(self.constraints.start_time):
            restaurant_categories = BREAKFAST_RESTAURANT_CATEGORIES
            random.shuffle(restaurant_categories)
        elif is_late_morning(self.constraints.start_time):
            restaurant_categories = BRUNCH_RESTAURANT_CATEGORIES
            random.shuffle(restaurant_categories)

        # If an activity has been selected, use that as the restaurant location restriction.
        if self.activity:






        self.restaurant = None
        return self.restaurant





    async def plan(self) -> OutingPlan:
        await self.plan_activity()
        await self.plan_restaurant()
        return OutingPlan(self.activity, self.restaurant)



# TODO: Remove test function.
async def main() -> None:
    test_outing_constraints = OutingConstraints(
        start_time = datetime.fromisoformat("2024-10-25T19:42:31.946205"),
        search_area_ids = ["us_ca_la_2"],
        budget = 3,
        headcount = 2,
    )
    test_category_1 = Category(id="103", subcategory_id="3008")
    test_category_2 = Category(id="103", subcategory_id="3012")
    test_category_3 = Category(id="105", subcategory_id="5001")
    test_category_4 = Category(id="103", subcategory_id="3008")
    test_category_5 = Category(id="103", subcategory_id="3013")
    test_category_6 = Category(id="104", subcategory_id="4007")
    test_user_1 = User(
        id=None,
        visitor_id=None,
        preferences=(UserPreferences(
            open_to_bars = True,
            requires_wheelchair_accessibility =True,
            restaurant_categories = [Category(id="sushi_restaurant"), Category(id="mexican_restaurant"), Category(id="american_restaurant"), Category(id="brazilian_restaurant")],
            activity_categories = [test_category_1, test_category_2, test_category_3],
        ))
    )
    test_user_2 = User(
        id="",
        visitor_id="",
        preferences=(UserPreferences(
            open_to_bars = True,
            requires_wheelchair_accessibility = False,
            restaurant_categories = [Category(id="chinese_restaurant"), Category(id="fast_food_restaurant"), Category(id="ice_cream_shop"), Category(id="mexican_restaurant")],
            activity_categories = [test_category_4, test_category_5, test_category_6],
        ))
    )

    outing = Outing([test_user_1, test_user_2], test_outing_constraints, None, None)
    plan = await outing.plan()


if __name__ == "__main__":
    asyncio.run(main())
