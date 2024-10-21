# TODO: Remove mock data imports
from mock_data import MockOutingConstraints, MockUser, MockPartner, MockVivialAPI, MockEventbriteAPI, MockGoogleAPI

from models import OutingPlan, OutingConstraints, User, EventbriteCategory, UserPreferences
import random








class Outing:
    constraints: OutingConstraints
    preferences: UserPreferences

    def __init__(self, constraints: OutingConstraints, group: list[User]) -> None:
        self.constraints = constraints
        self.preferences = self.combine_preferences(group)


    def combine_food_types(self, group: list[User]) -> list[str]:
        food_type_map = {}
        food_types_intersection = []
        food_types_difference = []

        for user in group:
            for type in user.preferences.google_food_types:
                if type not in food_type_map:
                    food_type_map[type] = 0
                food_type_map[type] += 1

        for type in food_type_map:
            if food_type_map[type] == len(group):
                food_types_intersection.append(type)
            else:
                food_types_difference.append(type)

        random.shuffle(food_types_intersection)
        random.shuffle(food_types_difference)

        return food_types_intersection + food_types_difference


    def combine_event_categories(self, group: list[User]) -> list[EventbriteCategory]:
        category_map = {}
        categories_intersection = []
        categories_difference = []

        for user in group:
            for category in user.preferences.eventbrite_categories:
                if category.id not in category_map:
                    category_map[category.id] = {}
                if category.subcategory_id not in category_map[category.id]:
                    category_map[category.id][category.subcategory_id] = 0
                category_map[category.id][category.subcategory_id] += 1

        for category_id in category_map:
            for subcategory_id in category_map[category_id]:
                if category_map[category_id][subcategory_id] == len(group):
                    categories_intersection.append(EventbriteCategory(id=category_id, subcategory_id=subcategory_id))
                else:
                    categories_difference.append(EventbriteCategory(id=category_id, subcategory_id=subcategory_id))

        random.shuffle(categories_intersection)
        random.shuffle(categories_difference)

        return categories_intersection + categories_difference


    def combine_preferences(self, group: list[User]) -> UserPreferences:
        google_food_types = self.combine_food_types(group)
        eventbrite_categories = self.combine_event_categories(group)
        requires_wheelchair_accessibility = False
        open_to_bars = True

        for user in group:
            if user.preferences.requires_wheelchair_accessibility:
                requires_wheelchair_accessibility = True
            if not user.preferences.open_to_bars:
                open_to_bars = False

        return UserPreferences(open_to_bars, requires_wheelchair_accessibility, google_food_types, eventbrite_categories)


    def plan(self) -> OutingPlan:
        return OutingPlan(restaurant={}, activity={})


# TODO: Remove test function.
def main() -> None:
    outing = Outing(MockOutingConstraints, [MockUser, MockPartner])
    outing.plan()

main()
