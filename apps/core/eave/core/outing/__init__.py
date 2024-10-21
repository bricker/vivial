# TODO: Remove mock data imports
from mock_data import MockOutingConstraints, MockUser, MockPartner, MockVivialAPI, MockEventbriteAPI, MockGoogleAPI

from models import OutingPlan, OutingConstraints, User, RestaurantCategory, ActivityCategory, UserPreferences

import random








class Outing:
    preferences: UserPreferences
    constraints: OutingConstraints

    # TODO: OutingActivity type.
    # TODO: OutingRestauraunt type.
    activity: object | None
    restaurant: object | None


    # TODO: OutingActivity type.
    # TODO: OutingRestauraunt type.
    def __init__(self, group: list[User], constraints: OutingConstraints, activity: object | None, restaurant: object | None) -> None:
        self.preferences = self.combine_preferences(group)
        self.constraints = constraints
        self.activity = activity
        self.restaurant = restaurant


    def combine_restaurant_categories(self, group: list[User]) -> list[RestaurantCategory]:
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


    def combine_activity_categories(self, group: list[User]) -> list[ActivityCategory]:
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



    # TODO: OutingActivity type.
    def plan_activity(self) -> object:

        return {}




    def get_plan(self) -> OutingPlan:
        print(self.preferences)

        return OutingPlan(self.activity, self.restaurant)

# TODO: Remove test function.
def main() -> None:
    outing = Outing([MockUser, MockPartner], MockOutingConstraints, None, None)
    # outing.plan_activity()
    # outing.plan_restaurant()
    outing.get_plan()


main()
