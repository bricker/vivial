# TODO: Remove mock data imports
from mock_data import MockOutingConstraints, MockUserPreferences, MockPartnerPreferences, MockVivialAPI, MockEventbriteAPI, MockGoogleAPI
from models import OutingPlan, OutingConstraints, UserPreferences










class Outing:
    constraints: OutingConstraints
    preferences: UserPreferences

    def __init__(self, constraints: OutingConstraints, all_preferences: list[UserPreferences]) -> None:
        self.constraints = constraints
        self.preferences = self.combine_preferences(all_preferences)





    def combine_preferences(self, all_preferences: list[UserPreferences]) -> UserPreferences:
        open_to_bars = True
        requires_wheelchair_accessibility = False
        google_food_types = []
        eventbrite_categories = []

        for preferences in all_preferences:
            # If anyone is closed to bars, omit bars for the group.

            # If anyone needs wheelchair accessibility, indicate this for the group.

            #





        return UserPreferences(open_to_bars, requires_wheelchair_accessibility, google_food_types, eventbrite_categories)









    def plan(self) -> OutingPlan:
        print("Planning outing...")
        return OutingPlan(restaurant={}, activity={})


# TODO: Remove test function.
def main():
    outing = Outing(MockOutingConstraints, [MockUserPreferences, MockPartnerPreferences])
    outing.plan()
main()
