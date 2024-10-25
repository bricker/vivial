
from budget import ACTIVITY_BUDGET_MAP, RESTAURANT_BUDGET_MAP
from models import OutingPlan, Restaurant, OutingConstraints, User, RestaurantCategory, ActivityCategory, UserPreferences, Activity
from dataclasses import dataclass




# from eave.core.areas.los_angeles import LOS_ANGELES_AREA_MAP
# TODO: remove temp hardcoding
@dataclass
class Radius:
    miles: float
    meters: float

@dataclass
class GeoArea:
    name: str
    key: str
    lat: float
    lon: float
    rad: Radius

us_ca_la_1 = GeoArea(name="Central LA & Hollywood", key="us_ca_la_1", lat=34.065730, lon=-118.323769, rad=(Radius(miles=5.78, meters=9302.008)))
us_ca_la_2 = GeoArea(name="Downtown Los Angeles", key="us_ca_la_2", lat=34.046422, lon=-118.245325, rad=(Radius(miles=1.69, meters=2719.791)))
us_ca_la_3 = GeoArea(name="Pasadena, Glendale, & Northeast LA", key="us_ca_la_3", lat=34.160040, lon=-118.209821, rad=(Radius(miles=6.49, meters=10444.64)))
us_ca_la_4 = GeoArea(name="Westside", key="us_ca_la_4", lat=33.965090, lon=-118.557344, rad=(Radius(miles=10.55, meters=16978.579)))
us_ca_la_5 = GeoArea(name="South Bay", key="us_ca_la_5", lat=33.856750, lon=-118.354487, rad=(Radius(miles=9.70, meters=15610.6)))
us_ca_la_6 = GeoArea(name="San Gabriel Valley", key="us_ca_la_6", lat=34.116746, lon=-118.016725, rad=(Radius(miles=8.46, meters=13615.05)))

LOS_ANGELES_AREA_MAP = {
    "us_ca_la_1": us_ca_la_1,
    "us_ca_la_2": us_ca_la_2,
    "us_ca_la_3": us_ca_la_3,
    "us_ca_la_4": us_ca_la_4,
    "us_ca_la_5": us_ca_la_5,
    "us_ca_la_6": us_ca_la_6,
}



from eave.stdlib.eventbrite.models.event import Event, EventStatus
from eave.stdlib.eventbrite.client import EventbriteClient
from eave.stdlib.google.google_places.client import GooglePlacesClient

from datetime import datetime, timedelta
import googlemaps
import random
import asyncio
import os


import pprint

class Outing:
    # googlemaps = googlemaps.Client(key=os.environ["GOOGLE_MAPS_API_KEY"])


    # TODO: remove to GOOGLE_PLACES_API_KEY
    places = GooglePlacesClient(api_key=os.environ["GOOGLE_MAPS_API_KEY"])
    eventbrite = EventbriteClient(api_key=os.environ["EVENTBRITE_API_KEY"])
    preferences: UserPreferences
    constraints: OutingConstraints
    activity: Activity | Event | None
    restaurant: Restaurant | None



    def __init__(self, group: list[User], constraints: OutingConstraints, activity: Activity | Event | None, restaurant: Restaurant | None) -> None:
        self.preferences = self.combine_preferences(group)
        self.constraints = constraints
        self.activity = activity
        self.restaurant = restaurant


    def combine_restaurant_categories(self, group: list[User]) -> list[RestaurantCategory]:
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
                intersection.append(RestaurantCategory(category_id))
            else:
                difference.append(RestaurantCategory(category_id))

        random.shuffle(intersection)
        random.shuffle(difference)
        return intersection + difference


    def combine_activity_categories(self, group: list[User]) -> list[ActivityCategory]:
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
                    intersection.append(ActivityCategory(category_id, subcategory_id))
                else:
                    difference.append(ActivityCategory(category_id, subcategory_id))

        random.shuffle(intersection)
        random.shuffle(difference)
        return intersection + difference


    def combine_preferences(self, group: list[User]) -> UserPreferences:
        restaurant_categories = self.combine_restaurant_categories(group)
        activity_categories = self.combine_activity_categories(group)
        requires_wheelchair_accessibility = False
        open_to_bars = True

        for user in group:
            if user.preferences.requires_wheelchair_accessibility:
                requires_wheelchair_accessibility = True
            if not user.preferences.open_to_bars:
                open_to_bars = False

        return UserPreferences(open_to_bars, requires_wheelchair_accessibility, restaurant_categories, activity_categories)


    async def plan_activity(self) -> Event | Activity | Restaurant | None:
        activity_start_time = self.constraints.start_time + timedelta(minutes=120)
        activity_end_time = activity_start_time + timedelta(minutes=120)
        random.shuffle(self.constraints.search_area_ids)

        # CASE 1: Recommend and Eventbrite event.
        for search_area_id in self.constraints.search_area_ids:
            for category in self.preferences.activity_categories:
                events = []
                # TODO: Fetch from internal database when that is ready (pending Bryan).
                # TODO: Pass in expansions: venue,ticket_availability.
                # events = get_eventbrite_events(
                #     search_area_id=search_area_id,
                #     category_id=category.id,
                #     subcategory_id=category.subcategory_id,
                #     start_time=activity_start_time,
                #     budget=ACTIVITY_BUDGET_MAP[self.constraints.budget]["max"],
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
                                    return Event(**event_details)

        # CASE 2: Recommend an activity from our manually curated database.
        for search_area_id in self.constraints.search_area_ids:
            for category in self.preferences.activity_categories:
                activities = []
                # TODO: Fetch from internal database when that is ready (pending Bryan).
                # activities = get_evergreen_activities(
                #     search_area_id=search_area_id,
                #     category_id=category.id,
                #     subcategory_id=category.subcategory_id,
                #     open_during=TimeInterval(activity_start_time, activity_end_time),
                #     budget=ACTIVITY_BUDGET_MAP[self.constraints.budget]["max"],
                # )
                # if len(activities) > 0:
                #     random.shuffle(activities)
                #     activity = activities[0]
                #     return Activity(activity**)





        # CASE 3: Recommend a bar as the activity if it's after 6:00 PM.

        # if self.preferences.open_to_bars and activity_start_time.hour >= 17:
        for search_area_id in self.constraints.search_area_ids:
            area = LOS_ANGELES_AREA_MAP[search_area_id]

            # print("about to fetch bars")
            nearby_sushi = await self.places.search_nearby(
                types=["sushi_restaurant"],
                lat=area.lat,
                lon=area.lon,
                radius=area.rad.meters,
            )
            # if results := nearby_sushi.get("results"):
            #     random.shuffle(results)
            #     for bar in results:
            #         # pprint.pp(bar)
            #         break


            # Check accessibility.
            # Check hours of operation.







        # CASE 4: No suitable activity was found :(
        return None









    async def get_plan(self) -> OutingPlan:
        return OutingPlan(self.activity, self.restaurant)



# TODO: Remove test function.
async def main() -> None:
    test_outing_constraints = OutingConstraints(
        start_time = datetime.fromisoformat("2024-10-20T01:00:00.000Z"),
        search_area_ids = ["us_ca_la_2"],
        budget = 3,
        headcount = 2,
    )
    test_category_1 = ActivityCategory(id="103", subcategory_id="3008")
    test_category_2 = ActivityCategory(id="103", subcategory_id="3012")
    test_category_3 = ActivityCategory(id="105", subcategory_id="5001")
    test_category_4 = ActivityCategory(id="103", subcategory_id="3008")
    test_category_5 = ActivityCategory(id="103", subcategory_id="3013")
    test_category_6 = ActivityCategory(id="104", subcategory_id="4007")
    test_user_1 = User(
        id=None,
        visitor_id=None,
        preferences=(UserPreferences(
            open_to_bars = True,
            requires_wheelchair_accessibility =False,
            restaurant_categories = [RestaurantCategory("sushi_restaurant"), RestaurantCategory("mexican_restaurant"), RestaurantCategory("american_restaurant"), RestaurantCategory("brazilian_restaurant")],
            activity_categories = [test_category_1, test_category_2, test_category_3],
        ))
    )
    test_user_2 = User(
        id="",
        visitor_id="",
        preferences=(UserPreferences(
            open_to_bars = True,
            requires_wheelchair_accessibility = False,
            restaurant_categories = [RestaurantCategory("chinese_restaurant"), RestaurantCategory("fast_food_restaurant"), RestaurantCategory("ice_cream_shop"), RestaurantCategory("mexican_restaurant")],
            activity_categories = [test_category_4, test_category_5, test_category_6],
        ))
    )

    outing = Outing([test_user_1, test_user_2], test_outing_constraints, None, None)
    await outing.plan_activity()
    # await outing.plan_restaurant()
    await outing.get_plan()


if __name__ == "__main__":
    asyncio.run(main())
