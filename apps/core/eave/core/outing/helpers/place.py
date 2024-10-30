from datetime import datetime, timedelta

from constants.restaurants import RESTAURANT_BUDGET_MAP
from constants.zoneinfo import LOS_ANGELES_ZONE_INFO

from eave.stdlib.google.places.models.place import Place


def place_will_be_open(place: Place, utc_arrival_time: datetime, utc_departure_time: datetime) -> bool:
    """
    Given a place from the Google Places API, determine whether or not that
    place will be open during the given time period.

    https://developers.google.com/maps/documentation/places/web-service/reference/rest/v1/places#OpeningHours
    """
    local_arrival_time = utc_arrival_time.astimezone(LOS_ANGELES_ZONE_INFO)
    local_departure_time = utc_departure_time.astimezone(LOS_ANGELES_ZONE_INFO)

    open_hours = place.get("regularOpeningHours")
    if open_hours is None:
        return False

    open_periods = open_hours.get("periods")
    if open_periods is None:
        return False

    for period in open_periods:
        if open := period.get("open"):
            is_relevant = open.get("day") == local_arrival_time.weekday()
            open_hour = open.get("hour")
            open_minute = open.get("minute")

            if is_relevant and open_hour is not None and open_minute is not None:
                open_time = local_arrival_time.replace(hour=open_hour, minute=open_minute)

                if close := period.get("close"):
                    close_hour = close.get("hour")
                    close_minute = close.get("minute")

                    if close_hour is not None and close_minute is not None:
                        close_time = local_arrival_time.replace(hour=close_hour, minute=close_minute)

                        if close.get("day") != local_arrival_time.weekday():
                            close_time = close_time + timedelta(days=1)  # Place closes the next day.

                        if open_time <= local_arrival_time and close_time >= local_departure_time:
                            return True
    return False


def place_is_in_budget(place: Place, budget: int) -> bool:
    """
    Given a place from the Google Places API, determine whether or not that
    place is within the user's budget for the date.

    https://developers.google.com/maps/documentation/places/web-service/reference/rest/v1/places#PriceLevel
    """
    return place.get("priceLevel") == RESTAURANT_BUDGET_MAP[budget]


def place_is_accessible(place: Place) -> bool:
    """
    Given a place from the Google Places API, determine whether or not that
    place is accessible for people in wheelchairs.

    https://developers.google.com/maps/documentation/places/web-service/reference/rest/v1/places#AccessibilityOptions
    """
    accessibility_options = place.get("accessibilityOptions")
    if accessibility_options is None:
        return False

    can_enter = accessibility_options.get("wheelchairAccessibleEntrance")
    can_park = accessibility_options.get("wheelchairAccessibleParking")
    can_pee = accessibility_options.get("wheelchairAccessibleRestroom")
    can_sit = accessibility_options.get("wheelchairAccessibleSeating")

    return bool(can_enter and can_park and can_pee and can_sit)
