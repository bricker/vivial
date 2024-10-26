from datetime import datetime
from eave.stdlib.google.places.models import accessibility_options
from eave.stdlib.google.places.models.place import Place
from constants import RESTAURANT_BUDGET_MAP

def place_will_be_open(place: Place, arrival_time: datetime, departure_time: datetime) -> bool:
    open_hours = place.get("regularOpeningHours")
    if open_hours is None:
        return False

    open_periods = open_hours.get("periods")
    if open_periods is None:
        return False

    relevant_periods = []
    for period in open_periods:
        if open := period.get("open"):
            day = open.get("day")
            if (day == arrival_time.weekday()):
                relevant_periods.append(period)

    if not relevant_periods:
        return False

    for period in relevant_periods:
        open = period.get("open")
        close = period.get("close")
        if open and close:
            open_hour = open.get("hour")
            open_minute = open.get("minute")
            if open_hour == arrival_time.hour and open_minute >= arrival_time.minute:
                return True

            if open_hour < arrival_time.hour:
                close_day = close.get("day")
                if close_day is not departure_time.day:
                    return True

                close_hour = close.get("hour")
                close_minute = close.get("minute")
                if close_hour == departure_time.hour and close_minute >= departure_time.minute:
                    return True

                if close_hour > departure_time.hour:
                    return True

    return False


def place_is_in_budget(place: Place, budget: int) -> bool:
    return place.get("priceLevel") == RESTAURANT_BUDGET_MAP[budget]


def place_is_accessible(place: Place, requires_wheelchair_accessibility: bool) -> bool:
    if not requires_wheelchair_accessibility:
        return True

    accessibility_options = place.get("accessibilityOptions")
    if accessibility_options is None:
        return False

    can_enter = accessibility_options.get("wheelchairAccessibleEntrance")
    can_park = accessibility_options.get("wheelchairAccessibleParking")
    can_pee = accessibility_options.get("wheelchairAccessibleRestroom")
    can_sit = accessibility_options.get("wheelchairAccessibleSeating")

    if can_enter and can_park and can_pee and can_sit:
        return True

    return False
