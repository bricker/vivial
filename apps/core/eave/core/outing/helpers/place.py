from collections.abc import MutableSequence
from datetime import datetime, timedelta

from google.maps.places_v1 import PlacesClient
from google.maps.places_v1.types import Place, SearchNearbyRequest

from ..constants.restaurants import RESTAURANT_BUDGET_MAP
from ..constants.zoneinfo import LOS_ANGELES_ZONE_INFO


def get_places_nearby(
    client: PlacesClient,
    latitude: float | str,
    longitude: float | str,
    radius_meters: float,
    included_primary_types: list[str],
    field_mask: str,
) -> MutableSequence[Place]:
    """
    Given a Google Places API client, use it to search for places nearby the
    given latitude and longitude that meet the given constraints.

    https://developers.google.com/maps/documentation/places/web-service/nearby-search
    """
    location_restriction = SearchNearbyRequest.LocationRestriction()
    location_restriction.circle.radius = radius_meters
    location_restriction.circle.center.latitude = latitude
    location_restriction.circle.center.longitude = longitude
    request = SearchNearbyRequest(
        location_restriction=location_restriction,
        included_primary_types=included_primary_types,
    )
    response = client.search_nearby(request=request, metadata=[("x-goog-fieldmask", field_mask)])
    return response.places or []


def place_will_be_open(place: Place, utc_arrival_time: datetime, utc_departure_time: datetime) -> bool:
    """
    Given a place from the Google Places API, determine whether or not that
    place will be open during the given time period.

    https://developers.google.com/maps/documentation/places/web-service/reference/rest/v1/places#OpeningHours
    """
    local_arrival_time = utc_arrival_time.astimezone(LOS_ANGELES_ZONE_INFO)
    local_departure_time = utc_departure_time.astimezone(LOS_ANGELES_ZONE_INFO)

    if place.regular_opening_hours is None:
        return False

    for period in place.regular_opening_hours.periods:
        is_relevant = period.open_ and (period.open_.day == local_arrival_time.weekday())

        if is_relevant and period.open_.hour is not None and period.open_.minute is not None:
            open_time = local_arrival_time.replace(hour=period.open_.hour, minute=period.open_.minute)

            if period.close and period.close.hour is not None and period.close.minute is not None:
                close_time = local_arrival_time.replace(hour=period.close.hour, minute=period.close.minute)

                if period.close.day != local_arrival_time.weekday():
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
    return place.price_level == RESTAURANT_BUDGET_MAP[budget]


def place_is_accessible(place: Place) -> bool:
    """
    Given a place from the Google Places API, determine whether or not that
    place is accessible for people in wheelchairs.

    https://developers.google.com/maps/documentation/places/web-service/reference/rest/v1/places#AccessibilityOptions
    """
    accessibility_options = place.accessibility_options
    if accessibility_options is None:
        return False

    can_enter = accessibility_options.wheelchair_accessible_entrance
    can_park = accessibility_options.wheelchair_accessible_parking
    can_pee = accessibility_options.wheelchair_accessible_restroom
    can_sit = accessibility_options.wheelchair_accessible_seating

    return bool(can_enter and can_park and can_pee and can_sit)
