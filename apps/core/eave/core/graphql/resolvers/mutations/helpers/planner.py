import random
import urllib.parse
from collections.abc import MutableSequence, Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import UUID
from zoneinfo import ZoneInfo

from geoalchemy2.functions import ST_DWithin
from google.maps.places_v1 import PlacesAsyncClient
from google.maps.places_v1.types import GetPlaceRequest, Place, SearchNearbyRequest
from sqlalchemy import func, or_

import eave.core.database
from eave.core.config import CORE_API_APP_CONFIG
from eave.core.graphql.types.activity import Activity, ActivitySource, ActivityVenue
from eave.core.graphql.types.location import Location
from eave.core.graphql.types.outing import OutingPreferencesInput
from eave.core.graphql.types.restaurant import Restaurant, RestaurantSource
from eave.core.lib.geo import Distance, GeoArea, GeoPoint
from eave.core.lib.time_category import is_early_evening, is_early_morning, is_late_evening, is_late_morning
from eave.core.orm.activity_category import ActivityCategoryOrm
from eave.core.orm.eventbrite_event import EventbriteEventOrm
from eave.core.orm.restaurant_category import MAGIC_BAR_RESTAURANT_CATEGORY_ID, RestaurantCategoryOrm
from eave.core.orm.search_region import SearchRegionOrm
from eave.core.orm.survey import SurveyOrm
from eave.core.shared.enums import OutingBudget
from eave.stdlib.eventbrite.client import EventbriteClient
from eave.stdlib.eventbrite.models.event import EventStatus
from eave.stdlib.logging import LOGGER

# You must pass a field mask to the Google Places API to specify the list of fields to return in the response.
# Reference: https://developers.google.com/maps/documentation/places/web-service/nearby-search
_RESTAURANT_FIELD_MASK = ",".join(
    [
        "places.id",
        "places.displayName",
        "places.accessibilityOptions",
        "places.addressComponents",
        "places.formattedAddress",
        "places.businessStatus",
        "places.googleMapsUri",
        "places.location",
        "places.photos",
        "places.primaryType",
        "places.primaryTypeDisplayName",
        "places.types",
        "places.nationalPhoneNumber",
        "places.priceLevel",
        "places.rating",
        "places.regularOpeningHours",
        "places.currentOpeningHours",
        "places.userRatingCount",
        "places.websiteUri",
        "places.reservable",
    ]
)

_BREAKFAST_GOOGLE_RESTAURANT_CATEGORY_IDS = (
    "coffee_shop",
    "breakfast_restaurant",
    "bakery",
    "cafe",
)

_BRUNCH_GOOGLE_RESTAURANT_CATEGORY_IDS = (
    "brunch_restaurant",
    "breakfast_restaurant",
    "cafe",
)


@dataclass(kw_only=True)
class PlannerResult:
    activity: Activity | None
    activity_start_time: datetime | None
    restaurant: Restaurant | None
    restaurant_arrival_time: datetime | None
    driving_time: str | None


def _combine_restaurant_categories(individual_preferences: list[OutingPreferencesInput]) -> list[RestaurantCategoryOrm]:
    """
    Given a group of users, combine their restaurant category preferences
    into one list of preferences.

    The preferences that the users have in common will always be at the
    front of the list.
    """
    category_map: dict[UUID, int] = {}
    intersection: list[RestaurantCategoryOrm] = []
    difference: list[RestaurantCategoryOrm] = []

    # Create a map of category IDs with occurence counts.
    for preferences in individual_preferences:
        for category_id in preferences.restaurant_category_ids:
            # Exclude the special "Bar" category
            if category_id != MAGIC_BAR_RESTAURANT_CATEGORY_ID:
                category_map.setdefault(category_id, 0)
                category_map[category_id] += 1

    # Use the map of category ID occurence counts to find the common categories.
    for category_id, num_matches in category_map.items():
        category = RestaurantCategoryOrm.one_or_exception(restaurant_category_id=category_id)
        if num_matches == len(individual_preferences):
            intersection.append(category)
        else:
            difference.append(category)

    random.shuffle(intersection)
    random.shuffle(difference)
    return intersection + difference


def _combine_activity_categories(individual_preferences: list[OutingPreferencesInput]) -> list[ActivityCategoryOrm]:
    """
    Given a group of users, combine their activity category preferences
    into one list of preferences.

    The preferences that the users have in common will always be at the
    front of the list.
    """
    category_map: dict[UUID, int] = {}
    intersection: list[ActivityCategoryOrm] = []
    difference: list[ActivityCategoryOrm] = []

    # Create a map of category / subcategory IDs with occurence counts.
    for preferences in individual_preferences:
        for category_id in preferences.activity_category_ids:
            category_map.setdefault(category_id, 0)
            category_map[category_id] += 1

    # Use the map of category / subcategory ID occurence counts to find the common categories.
    for category_id, num_matches in category_map.items():
        category = ActivityCategoryOrm.one_or_exception(activity_category_id=category_id)
        if num_matches == len(individual_preferences):
            intersection.append(category)
        else:
            difference.append(category)

    random.shuffle(intersection)
    random.shuffle(difference)
    return intersection + difference


def _combine_bar_openness(individual_preferences: list[OutingPreferencesInput]) -> bool:
    """
    Given a group of users, return False if any of the users is not open to
    going to a bar.
    """
    return all(
        MAGIC_BAR_RESTAURANT_CATEGORY_ID in preferences.restaurant_category_ids
        for preferences in individual_preferences
    )


class OutingPlanner:
    """
    Use this class to plan an outing for a group of users based on their outing
    constraints and personal preferences.

    Currently, an outing consists of food and a thing - eat at a well-rated
    restaurant, then go to an event or engage in a cute activity.
    """

    places: PlacesAsyncClient
    eventbrite: EventbriteClient
    survey: SurveyOrm
    activity: Activity | None
    restaurant: Restaurant | None
    activity_start_time_local: datetime | None
    restaurant_arrival_time_local: datetime | None

    group_restaurant_category_preferences: list[RestaurantCategoryOrm]
    group_activity_category_preferences: list[ActivityCategoryOrm]
    group_open_to_bars: bool

    def __init__(
        self,
        individual_preferences: list[OutingPreferencesInput],
        survey: SurveyOrm,
        activity: Activity | None = None,
        restaurant: Restaurant | None = None,
        activity_start_time: datetime | None = None,
        restaurant_arrival_time: datetime | None = None,
    ) -> None:
        self.places = PlacesAsyncClient()
        self.eventbrite = EventbriteClient(api_key=CORE_API_APP_CONFIG.eventbrite_api_key)
        self.survey = survey
        self.activity = activity
        self.restaurant = restaurant
        self.activity_start_time_local = activity_start_time.astimezone(survey.timezone) if activity_start_time else None
        self.restaurant_arrival_time_local = restaurant_arrival_time.astimezone(survey.timezone) if restaurant_arrival_time else None

        self.group_restaurant_category_preferences = _combine_restaurant_categories(individual_preferences)
        self.group_activity_category_preferences = _combine_activity_categories(individual_preferences)
        self.group_open_to_bars = _combine_bar_openness(individual_preferences)

    async def plan_activity(self) -> Activity | None:
        """
        Plan an activity for the outing, taking into consideration the outing
        constraints and group preferences.

        For now, the activity always happens after a meal. We plan the activity
        first, then we find a restaurant nearby that users can eat at before
        the activity.
        """

        # The time+120 minutes is because the restaurant happens before the activity.
        start_time_local = self.survey.start_time_local + timedelta(minutes=120)
        self.activity_start_time_local = start_time_local
        end_time_local = start_time_local + timedelta(minutes=90)
        random.shuffle(self.survey.search_area_ids)

        within_areas = [
            SearchRegionOrm.one_or_exception(search_region_id=search_area_id).area
            for search_area_id in self.survey.search_area_ids
        ]

        # CASE 1: Recommend an Eventbrite event.
        query = EventbriteEventOrm.select(
            time_range_contains=start_time_local,
            cost_range_contains=self.survey.budget.upper_limit_cents,
            within_areas=within_areas,
            vivial_activity_category_ids=[cat.id for cat in self.group_activity_category_preferences],
        ).order_by(func.random())

        async with eave.core.database.async_session.begin() as db_session:
            results = await db_session.scalars(query)

            for event in results:
                try:
                    event_details = await self.eventbrite.get_event_by_id(event_id=event.eventbrite_event_id)

                    if not (ticket_availability := event_details.get("ticket_availability")):
                        LOGGER.warning(
                            "Missing ticket_availability; excluding event.",
                            {"eventbrite_event_id": event.eventbrite_event_id},
                        )
                        continue

                    if not ticket_availability.get("has_available_tickets"):
                        LOGGER.warning(
                            "has_available_tickets=False; excluding event.",
                            {"eventbrite_event_id": event.eventbrite_event_id},
                        )
                        continue

                    if not (event_name := event_details.get("name")):
                        LOGGER.warning(
                            "event name missing; excluding event.",
                            {"eventbrite_event_id": event.eventbrite_event_id},
                        )
                        continue

                    if event_details.get("status") != EventStatus.LIVE:
                        LOGGER.warning(
                            "status != live; excluding event.", {"eventbrite_event_id": event.eventbrite_event_id}
                        )
                        continue

                    if not (venue := event_details.get("venue")):
                        LOGGER.warning(
                            "Missing venue; excluding event.", {"eventbrite_event_id": event.eventbrite_event_id}
                        )
                        continue

                    if (venue_address := venue.get("address")) is None:
                        LOGGER.warning(
                            "Missing venue address; excluding event.",
                            {"eventbrite_event_id": event.eventbrite_event_id},
                        )
                        continue

                    if (venue_formatted_address := venue_address.get("localized_address_display")) is None:
                        LOGGER.warning(
                            "Missing venue localized_address_display; excluding event.",
                            {"eventbrite_event_id": event.eventbrite_event_id},
                        )
                        continue

                    if (venue_lat := venue.get("latitude")) is None:
                        LOGGER.warning(
                            "Missing venue latitude; excluding event.",
                            {"eventbrite_event_id": event.eventbrite_event_id},
                        )
                        continue

                    if (venue_lon := venue.get("longitude")) is None:
                        LOGGER.warning(
                            "Missing venue longitude; excluding event.",
                            {"eventbrite_event_id": event.eventbrite_event_id},
                        )
                        continue

                    description = await self.eventbrite.get_event_description(event_id=event.eventbrite_event_id)
                    event_details["description"] = description

                    self.activity = Activity(
                        source_id=str(event.id),
                        source=ActivitySource.EVENTBRITE,
                        name=event_name["text"],
                        description=event_details["description"]["text"],
                        photos=None,  # TODO
                        ticket_info=None,  # TODO
                        venue=ActivityVenue(
                            name=venue["name"],
                            location=Location(
                                directions_uri=google_maps_directions_url(venue_formatted_address),
                                latitude=float(venue_lat),
                                longitude=float(venue_lon),
                                formatted_address=venue_formatted_address,
                            ),
                        ),
                        website_uri=event_details.get("vanity_url"),
                        door_tips=None,
                        insider_tips=None,
                        parking_tips=None,
                    )
                    return self.activity

                except Exception as e:
                    LOGGER.exception(e)
                    continue

        # CASE 2: Recommend an "evergreen" activity from our manually curated database.
        # for search_area_id in self.constraints.search_area_ids:
        #     for category in self.preferences.activity_categories:
        #         activities = []
        # TODO: Fetch from internal database when that is ready (pending Bryan).
        # activities = get_evergreen_activities(
        #     search_area_id=search_area_id,
        #     category_id=category.id,
        #     subcategory_id=category.subcategory_id,
        #     start_time=activity_start_time,
        #     end_time=activity_end_time,
        #     budget=ACTIVITY_BUDGET_MAP[self.constraints.budget],
        # )
        # if len(activities):
        #     random.shuffle(activities)
        #     geo_location = GeoLocation(TODO)
        #     self.activity = OutingComponent(TODO)
        #     return self.activity

        # CASE 3: Recommend a bar or an ice cream shop as a fallback activity.
        is_evening = is_early_evening(self.survey.start_time_utc, self.survey.timezone) or is_late_evening(self.survey.start_time_utc, self.survey.timezone)
        place_type = "ice_cream_shop"
        if is_evening and self.group_open_to_bars:
            place_type = "bar"

        for search_area_id in self.survey.search_area_ids:
            region = SearchRegionOrm.one_or_exception(search_region_id=search_area_id)
            places_nearby = await get_places_nearby(
                client=self.places,
                area=region.area,
                included_primary_types=[place_type],
                field_mask=_RESTAURANT_FIELD_MASK,
            )
            random.shuffle(places_nearby)
            for place in places_nearby:
                will_be_open = place_will_be_open(place=place, arrival_time=start_time_local, departure_time=end_time_local, timezone=self.survey.timezone)
                is_in_budget = place_is_in_budget(place, self.survey.budget)
                if will_be_open and is_in_budget and place.location:
                    venue_lat = place.location.latitude
                    venue_lon = place.location.longitude
                    if venue_lat and venue_lon:
                        self.activity = Activity(
                            source_id=place.id,
                            source=ActivitySource.GOOGLE_PLACES,
                            name=place.display_name,
                            description=place.editorial_summary,
                            photos=None,  # TODO
                            ticket_info=None,  # TODO
                            venue=ActivityVenue(
                                name=place.display_name,
                                location=Location(
                                    directions_uri=place.google_maps_uri,
                                    latitude=venue_lat,
                                    longitude=venue_lon,
                                    formatted_address=place.formatted_address,
                                ),
                            ),
                            website_uri=place.website_uri,
                            door_tips=None,
                            insider_tips=None,
                            parking_tips=None,
                        )

                        return self.activity

        # CASE 4: No suitable activity was found :(
        self.activity = None
        return self.activity

    async def plan_restaurant(self) -> Restaurant | None:
        """
        Plan a restaurant for the outing, taking into consideration the outing
        activity, outing constraints and group preferences.

        For now, the meal always happens before the activity.
        """
        arrival_time_local = self.survey.start_time_local
        self.restaurant_arrival_time_local = arrival_time_local
        departure_time_local = arrival_time_local + timedelta(minutes=90)
        search_areas = []

        # If this is a morning outing, override user restaurant preferences and show them breakfast / brunch spots.
        if is_early_morning(arrival_time_local, self.survey.timezone):
            google_category_ids = list(_BREAKFAST_GOOGLE_RESTAURANT_CATEGORY_IDS)
            random.shuffle(google_category_ids)
        elif is_late_morning(arrival_time_local, self.survey.timezone):
            google_category_ids = list(_BRUNCH_GOOGLE_RESTAURANT_CATEGORY_IDS)
            random.shuffle(google_category_ids)
        else:
            # Already randomized in combiner funcs
            google_category_ids = [
                gcid for cat in self.group_restaurant_category_preferences for gcid in cat.google_category_ids
            ]

        # If an activity has been selected, use that as the search area.
        if self.activity:
            search_areas = [
                GeoArea(
                    center=GeoPoint(
                        lat=self.activity.venue.location.latitude, lon=self.activity.venue.location.longitude
                    ),
                    rad=Distance(miles=5),
                ),
            ]

        # TODO: Sort areas by distance to the activity location.
        for search_area_id in self.survey.search_area_ids:
            search_areas.append(SearchRegionOrm.one_or_exception(search_region_id=search_area_id).area)

        # Find a restaurant that meets the outing constraints.
        for area in search_areas:
            restaurants_nearby = await get_places_nearby(
                client=self.places,
                area=area,
                included_primary_types=google_category_ids,
                field_mask=_RESTAURANT_FIELD_MASK,
            )
            random.shuffle(restaurants_nearby)
            for restaurant in restaurants_nearby:
                will_be_open = place_will_be_open(place=restaurant, arrival_time=arrival_time_local, departure_time=departure_time_local, timezone=self.survey.timezone)
                is_in_budget = place_is_in_budget(restaurant, self.survey.budget)
                if will_be_open and is_in_budget:
                    if restaurant.location:
                        lat = restaurant.location.latitude
                        lon = restaurant.location.longitude
                        if lat and lon:
                            self.restaurant = Restaurant(
                                source_id=restaurant.id,
                                source=RestaurantSource.GOOGLE_PLACES,
                                location=Location(
                                    latitude=lat,
                                    longitude=lon,
                                    formatted_address=restaurant.formatted_address,
                                    directions_uri=restaurant.google_maps_uri,
                                ),
                                photos=None,  # TODO
                                name=restaurant.display_name,
                                reservable=restaurant.reservable,
                                rating=restaurant.rating,
                                primary_type_name=restaurant.primary_type_display_name,
                                website_uri=restaurant.website_uri,
                                description=restaurant.editorial_summary,
                                parking_tips=None,
                                customer_favorites=None,
                            )
                            return self.restaurant

        # No restaurant was found :(
        self.restaurant = None
        return self.restaurant

    async def plan(self) -> PlannerResult:
        """
        Plan an outing for a group of users, taking into consideration outing
        constraints and group preferences.
        """
        await self.plan_activity()
        await self.plan_restaurant()
        return PlannerResult(
            activity=self.activity,
            activity_start_time=self.activity_start_time_local,
            restaurant=self.restaurant,
            restaurant_arrival_time=self.restaurant_arrival_time_local,
            driving_time=None,
        )


async def get_place(
    client: PlacesAsyncClient,
    id: str,
) -> Place:
    return await client.get_place(request=GetPlaceRequest(name=f"places/{id}"))


async def get_places_nearby(
    client: PlacesAsyncClient,
    area: GeoArea,
    included_primary_types: Sequence[str],
    field_mask: str,
) -> MutableSequence[Place]:
    """
    Given a Google Places API client, use it to search for places nearby the
    given latitude and longitude that meet the given constraints.

    https://developers.google.com/maps/documentation/places/web-service/nearby-search
    """
    location_restriction = SearchNearbyRequest.LocationRestriction()
    location_restriction.circle.radius = area.rad.meters
    location_restriction.circle.center.latitude = area.center.lat
    location_restriction.circle.center.longitude = area.center.lon
    request = SearchNearbyRequest(
        location_restriction=location_restriction,
        included_primary_types=included_primary_types[0:50],
    )
    response = await client.search_nearby(request=request, metadata=[("x-goog-fieldmask", field_mask)])
    return response.places or []


def place_will_be_open(*, place: Place, arrival_time: datetime, departure_time: datetime, timezone: ZoneInfo) -> bool:
    """
    Given a place from the Google Places API, determine whether or not that
    place will be open during the given time period.

    https://developers.google.com/maps/documentation/places/web-service/reference/rest/v1/places#OpeningHours
    """
    if place.regular_opening_hours is None:
        return False

    arrival_time_local = arrival_time.astimezone(timezone)
    departure_time_local = departure_time.astimezone(timezone)

    for period in place.regular_opening_hours.periods:
        is_relevant = period.open_ and (period.open_.day == arrival_time_local.weekday())

        if is_relevant and period.open_.hour is not None and period.open_.minute is not None:
            open_time = arrival_time_local.replace(hour=period.open_.hour, minute=period.open_.minute)

            if period.close and period.close.hour is not None and period.close.minute is not None:
                close_time = arrival_time_local.replace(hour=period.close.hour, minute=period.close.minute)

                if period.close.day != arrival_time_local.weekday():
                    close_time = close_time + timedelta(days=1)  # Place closes the next day.

                if open_time <= arrival_time_local and close_time >= departure_time_local:
                    return True
    return False


def place_is_in_budget(place: Place, budget: OutingBudget) -> bool:
    """
    Given a place from the Google Places API, determine whether or not that
    place is within the user's budget for the date.

    https://developers.google.com/maps/documentation/places/web-service/reference/rest/v1/places#PriceLevel
    """
    return place.price_level == budget.google_places_price_level


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

    return can_enter and can_park and can_pee and can_sit


def google_maps_directions_url(address: str) -> str:
    urlsafe_addr = urllib.parse.quote_plus(address)
    return f"https://www.google.com/maps/place/{urlsafe_addr}"
