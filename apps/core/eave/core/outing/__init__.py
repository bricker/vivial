from eave.stdlib.eventbrite.models import ticket_availability
from budget import ACTIVITY_BUDGET_MAP, RESTAURANT_BUDGET_MAP
from models import OutingPlan, OutingRestaurant, OutingConstraints, User, RestaurantCategory, ActivityCategory, UserPreferences, Activity, Location
from eave.stdlib.eventbrite.models.event import Event, EventStatus
from eave.stdlib.eventbrite.client import EventbriteClient

from datetime import date, datetime, timedelta
import random
import asyncio
import os

class Outing:
    eventbrite_client: EventbriteClient
    preferences: UserPreferences
    constraints: OutingConstraints
    activity: Activity | Event | None
    restaurant: OutingRestaurant | None


    async def __init__(self, group: list[User], constraints: OutingConstraints, activity: OutingActivity | None, restaurant: OutingRestaurant | None) -> None:
        self.eventbrite_client = EventbriteClient(api_key=os.environ["EVENTBRITE_API_KEY"])
        self.preferences = await self.combine_preferences(group)
        self.constraints = constraints
        self.activity = activity
        self.restaurant = restaurant


    async def combine_restaurant_categories(self, group: list[User]) -> list[RestaurantCategory]:
        category_map = {}
        categories_intersection = []
        categories_difference = []

        for user in group:
            for category in user.preferences.restaurant_categories:
                if category.id not in category_map:
                    category_map[category.id] = 0
                category_map[category.id] += 1

        for category_id in category_map:
            if category_map[category_id] == len(group):
                categories_intersection.append(RestaurantCategory(category_id))
            else:
                categories_difference.append(RestaurantCategory(category_id))

        random.shuffle(categories_intersection)
        random.shuffle(categories_difference)

        return categories_intersection + categories_difference


    async def combine_activity_categories(self, group: list[User]) -> list[ActivityCategory]:
        category_map = {}
        categories_intersection = []
        categories_difference = []

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
                    categories_intersection.append(ActivityCategory(category_id, subcategory_id))
                else:
                    categories_difference.append(ActivityCategory(category_id, subcategory_id))

        random.shuffle(categories_intersection)
        random.shuffle(categories_difference)

        return categories_intersection + categories_difference


    async def combine_preferences(self, group: list[User]) -> UserPreferences:
        restaurant_categories = await self.combine_restaurant_categories(group)
        activity_categories = await self.combine_activity_categories(group)
        requires_wheelchair_accessibility = False
        open_to_bars = True

        for user in group:
            if user.preferences.requires_wheelchair_accessibility:
                requires_wheelchair_accessibility = True
            if not user.preferences.open_to_bars:
                open_to_bars = False

        return UserPreferences(open_to_bars, requires_wheelchair_accessibility, restaurant_categories, activity_categories)




    async def plan_activity(self) -> Event | Activity | None:
        activity_start_time = self.constraints.start_time + timedelta(minutes=120)
        activity_end_time = activity_start_time + timedelta(minutes=120)
        random.shuffle(self.constraints.search_area_ids)

        # Case 1: Recommend and Eventbrite event.
        for search_area_id in self.constraints.search_area_ids:
            for category in self.preferences.activity_categories:
                events = []
                # TODO: Fetch from internal database when that is ready (pending Bryan).
                # events = get_eventbrite_events(
                #     search_area_id=search_area_id,
                #     category_id=category.id,
                #     subcategory_id=category.subcategory_id,
                #     start_time=activity_start_time,
                #     cost=ACTIVITY_BUDGET_MAP[self.constraints.budget]["max"],
                # )
                random.shuffle(events)
                for event in events:
                    if event_details := await self.eventbrite_client.get_event_by_id(event_id=event.id):
                        if ticket_availability := event_details.get("ticket_availability"):
                            has_available_tickets = ticket_availability.get("has_available_tickets")
                            is_live = event_details.get("status") == EventStatus.live
                            if has_available_tickets and is_live:
                                return Event(**event_details)


        # Case 2: Recommend an activity from our manually curated database.
        for search_area_id in self.constraints.search_area_ids:
            for category in self.preferences.activity_categories:
                activities = []
                # TODO: Fetch from internal database when that is ready (pending Bryan).
                # activities = get_evergreen_activities(
                #     search_area_id=search_area_id,
                #     category_id=category.id,
                #     subcategory_id=category.subcategory_id,
                #     open_during=TimeInterval(activity_start_time, activity_end_time),
                #     cost=ACTIVITY_BUDGET_MAP[self.constraints.budget]["max"],
                # )
                if len(activities) > 0:
                    random.shuffle(activities)
                    activity = activities[0]
                    # TODO: Flesh out what data is returned to client (pending Lana).
                    return OutingActivity(search_area_id)


        # Case 3: Recommend a bar if it's after 6:00 PM.
        if self.preferences.open_to_bars and activity_start_time.hour >= 17:

            # Recommend a cocktail lounge.
            # Check accessibility.
            # Check hours of operation.



        # Case 4: No suitable activity was found :(
        return None









    async def get_plan(self) -> OutingPlan:
        return OutingPlan(self.activity, self.restaurant)



# TODO: Remove test function.
async def main() -> None:
    test_outing_constraints = OutingConstraints(
        start_time = datetime.fromisoformat("2024-10-20T01:00:00.000Z"),
        search_area_ids = [],
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
