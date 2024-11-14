import random
from collections.abc import MutableSequence, Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import UUID

from geoalchemy2.functions import ST_DWithin
from google.maps import places_v1
from sqlalchemy import func, or_

import eave.core.database
from eave.core.config import CORE_API_APP_CONFIG
from eave.core.graphql.resolvers.mutations.plan_outing import PlanOutingInput
from eave.core.graphql.types.activity import Activity, ActivitySource, ActivityVenue
from eave.core.graphql.types.location import Location
from eave.core.graphql.types.outing import ProposedOuting
from eave.core.graphql.types.preferences import Preferences
from eave.core.graphql.types.restaurant import Restaurant, RestaurantSource
from eave.core.lib.geo import Distance, GeoArea, GeoPoint
from eave.core.lib.time_category import is_early_evening, is_early_morning, is_late_evening, is_late_morning
from eave.core.orm.activity_subcategory import ActivitySubcategoryOrm
from eave.core.orm.eventbrite_event import EventbriteEventOrm
from eave.core.orm.restaurant_category import RestaurantCategoryOrm
from eave.core.orm.search_region import SearchRegionOrm
from eave.core.shared.enums import OutingBudget
from eave.core.zoneinfo import LOS_ANGELES_ZONE_INFO
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

_BREAKFAST_RESTAURANT_CATEGORY_IDS = (
    "coffee_shop",
    "breakfast_restaurant",
    "bakery",
    "cafe",
)

_BRUNCH_RESTAURANT_CATEGORY_IDS = (
    "brunch_restaurant",
    "breakfast_restaurant",
    "cafe",
)


@dataclass(kw_only=True)
class GroupPreferences:
    open_to_bars: bool
    requires_wheelchair_accessibility: bool
    restaurant_categories: list[RestaurantCategoryOrm]
    activity_categories: list[ActivitySubcategoryOrm]


def _combine_restaurant_categories(group: list[Preferences]) -> list[RestaurantCategoryOrm]:
    """
    Given a group of users, combine their restaurant category preferences
    into one list of preferences.

    The preferences that the users have in common will always be at the
    front of the list.
    """
    category_map: dict[UUID, int] = {}
    intersection: list[RestaurantCategoryOrm] = []
    difference: list[RestaurantCategoryOrm] = []

    # Create a map of category IDs with occurance counts.
    for preferences in group:
        for category in preferences.restaurant_categories:
            category_map.setdefault(category.id, 0)
            category_map[category.id] += 1

    # Use the map of category ID occurance counts to find the common categories.
    for category_id, num_matches in category_map.items():
        category = RestaurantCategoryOrm.one_or_exception(restaurant_category_id=category_id)
        if num_matches == len(group):
            intersection.append(category)
        else:
            difference.append(category)

    random.shuffle(intersection)
    random.shuffle(difference)
    return intersection + difference


def _combine_activity_categories(group: list[Preferences]) -> list[ActivitySubcategoryOrm]:
    """
    Given a group of users, combine their activity category preferences
    into one list of preferences.

    The preferences that the users have in common will always be at the
    front of the list.
    """
    category_map: dict[UUID, int] = {}
    intersection: list[ActivitySubcategoryOrm] = []
    difference: list[ActivitySubcategoryOrm] = []

    # Create a map of category / subcategory IDs with occurence counts.
    for preferences in group:
        for category in preferences.activity_categories:
            category_map.setdefault(category.id, 0)
            category_map[category.id] += 1

    # Use the map of category / subcategory ID occurence counts to find the common categories.
    for category_id, num_matches in category_map.items():
        category = ActivitySubcategoryOrm.one_or_exception(activity_subcategory_id=category_id)
        if num_matches == len(group):
            intersection.append(category)
        else:
            difference.append(category)

    random.shuffle(intersection)
    random.shuffle(difference)
    return intersection + difference


def _combine_wheelchair_needs(group: list[Preferences]) -> bool:
    """
    Given a group of users, return True if any of the users requires
    wheelchair accessibility.
    """
    return any(preferences.requires_wheelchair_accessibility for preferences in group)


def _combine_bar_openness(group: list[Preferences]) -> bool:
    """
    Given a group of users, return False if any of the users is not open to
    going to a bar.
    """
    return all(preferences.open_to_bars for preferences in group)


def _combine_preferences(group: list[Preferences]) -> GroupPreferences:
    """
    Given a group of users, combine their outing preferences. The logic
    throughout this class gives priority to common preferences.
    """
    return GroupPreferences(
        restaurant_categories=_combine_restaurant_categories(group),
        activity_categories=_combine_activity_categories(group),
        requires_wheelchair_accessibility=_combine_wheelchair_needs(group),
        open_to_bars=_combine_bar_openness(group),
    )


class OutingPlanner:
    """
    Use this class to plan an outing for a group of users based on their outing
    constraints and personal preferences.

    Currently, an outing consists of food and a thing - eat at a well-rated
    restaurant, then go to an event or engage in a cute activity.
    """

    places: places_v1.PlacesClient
    eventbrite: EventbriteClient
    constraints: PlanOutingInput
    activity: Activity | None
    restaurant: Restaurant | None

    group_preferences: GroupPreferences

    def __init__(
        self,
        group: list[Preferences],
        constraints: PlanOutingInput,
        activity: Activity | None = None,
        restaurant: Restaurant | None = None,
    ) -> None:
        self.places = places_v1.PlacesClient()
        self.eventbrite = EventbriteClient(api_key=CORE_API_APP_CONFIG.eventbrite_api_key)
        self.constraints = constraints
        self.activity = activity
        self.restaurant = restaurant
        self.group_preferences = _combine_preferences(group)

    async def plan_activity(self) -> Activity | None:
        """
        Plan an activity for the outing, taking into consideration the outing
        constraints and group preferences.

        For now, the activity always happens after a meal. We plan the activity
        first, then we find a restaurant nearby that users can eat at before
        the activity.
        """
        activity_start_time = self.constraints.start_time + timedelta(minutes=120)
        activity_end_time = activity_start_time + timedelta(minutes=90)
        random.shuffle(self.constraints.search_area_ids)

        within_areas = [
            SearchRegionOrm.one_or_exception(search_region_id=search_area_id).area
            for search_area_id in self.constraints.search_area_ids
        ]

        # CASE 1: Recommend an Eventbrite event.
        query = (
            EventbriteEventOrm.select()
            .where(EventbriteEventOrm.time_range.contains(activity_start_time))
            .where(EventbriteEventOrm.cost_cents_range.contains(self.constraints.budget.upper_limit_cents))
            .where(
                or_(
                    *[
                        ST_DWithin(EventbriteEventOrm.coordinates, area.center.geoalchemy_shape(), area.rad.meters)
                        for area in within_areas
                    ]
                )
            )
            .where(
                or_(
                    *[EventbriteEventOrm.subcategory_id == cat.id for cat in self.group_preferences.activity_categories]
                )
            )
            .order_by(func.random())
        )

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
                        source=ActivitySource.EVENTBRITE,
                        name=event_name["text"],
                        description=event_details["description"]["text"],
                        photos=None,
                        ticket_info=None,
                        venue=ActivityVenue(
                            name=venue["name"],
                            location=Location(
                                directions_uri="https://www.google.com/",  # FIXME
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
        is_evening = is_early_evening(activity_start_time) or is_late_evening(activity_start_time)
        place_type = "ice_cream_shop"
        if is_evening and self.group_preferences.open_to_bars:
            place_type = "bar"

        for search_area_id in self.constraints.search_area_ids:
            region = SearchRegionOrm.one_or_exception(search_region_id=search_area_id)
            places_nearby = get_places_nearby(
                client=self.places,
                area=region.area,
                included_primary_types=[place_type],
                field_mask=_RESTAURANT_FIELD_MASK,
            )
            random.shuffle(places_nearby)
            for place in places_nearby:
                if self.group_preferences.requires_wheelchair_accessibility and not place_is_accessible(place):
                    continue
                will_be_open = place_will_be_open(place, activity_start_time, activity_end_time)
                is_in_budget = place_is_in_budget(place, self.constraints.budget)
                if will_be_open and is_in_budget and place.location:
                    venue_lat = place.location.latitude
                    venue_lon = place.location.longitude
                    if venue_lat and venue_lon:
                        self.activity = Activity(
                            source=ActivitySource.GOOGLE_PLACES,
                            name=place.display_name,
                            description=place.editorial_summary,
                            photos=None,
                            ticket_info=None,
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
        arrival_time = self.constraints.start_time
        departure_time = arrival_time + timedelta(minutes=90)
        search_areas = []

        local_timestamp = self.constraints.start_time.astimezone(LOS_ANGELES_ZONE_INFO)
        # If this is a morning outing, override user restaurant preferences and show them breakfast / brunch spots.
        if is_early_morning(local_timestamp):
            restaurant_category_ids = list(_BREAKFAST_RESTAURANT_CATEGORY_IDS)
            random.shuffle(restaurant_category_ids)
        elif is_late_morning(local_timestamp):
            restaurant_category_ids = list(_BRUNCH_RESTAURANT_CATEGORY_IDS)
            random.shuffle(restaurant_category_ids)
        else:
            # Already randomized in combiner funcs
            restaurant_category_ids = [
                gcid for cat in self.group_preferences.restaurant_categories for gcid in cat.google_category_ids
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
        for search_area_id in self.constraints.search_area_ids:
            search_areas.append(SearchRegionOrm.one_or_exception(search_region_id=search_area_id).area)

        # Find a restaurant that meets the outing constraints.
        for area in search_areas:
            restaurants_nearby = get_places_nearby(
                client=self.places,
                area=area,
                included_primary_types=restaurant_category_ids,
                field_mask=_RESTAURANT_FIELD_MASK,
            )
            random.shuffle(restaurants_nearby)
            for restaurant in restaurants_nearby:
                if self.group_preferences.requires_wheelchair_accessibility and not place_is_accessible(restaurant):
                    continue
                will_be_open = place_will_be_open(restaurant, arrival_time, departure_time)
                is_in_budget = place_is_in_budget(restaurant, self.constraints.budget)
                if will_be_open and is_in_budget:
                    if restaurant.location:
                        lat = restaurant.location.latitude
                        lon = restaurant.location.longitude
                        if lat and lon:
                            self.restaurant = Restaurant(
                                source=RestaurantSource.GOOGLE_PLACES,
                                location=Location(
                                    latitude=lat,
                                    longitude=lon,
                                    formatted_address=restaurant.formatted_address,
                                    directions_uri=restaurant.google_maps_uri,
                                ),
                                photos=None,
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

    async def plan(self) -> ProposedOuting:
        """
        Plan an outing for a group of users, taking into consideration outing
        constraints and group preferences.
        """
        await self.plan_activity()
        await self.plan_restaurant()
        return ProposedOuting(
            activity=self.activity,
            activity_start_time=None,
            restaurant=self.restaurant,
            restaurant_arrival_time=None,
            driving_time=None,
        )


def get_places_nearby(
    client: places_v1.PlacesClient,
    area: GeoArea,
    included_primary_types: Sequence[str],
    field_mask: str,
) -> MutableSequence[places_v1.Place]:
    """
    Given a Google Places API client, use it to search for places nearby the
    given latitude and longitude that meet the given constraints.

    https://developers.google.com/maps/documentation/places/web-service/nearby-search
    """
    location_restriction = places_v1.SearchNearbyRequest.LocationRestriction()
    location_restriction.circle.radius = area.rad.meters
    location_restriction.circle.center.latitude = area.center.lat
    location_restriction.circle.center.longitude = area.center.lon
    request = places_v1.SearchNearbyRequest(
        location_restriction=location_restriction,
        included_primary_types=included_primary_types[0:50],
    )
    response = client.search_nearby(request=request, metadata=[("x-goog-fieldmask", field_mask)])
    return response.places or []


def place_will_be_open(place: places_v1.Place, utc_arrival_time: datetime, utc_departure_time: datetime) -> bool:
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


def place_is_in_budget(place: places_v1.Place, budget: OutingBudget) -> bool:
    """
    Given a place from the Google Places API, determine whether or not that
    place is within the user's budget for the date.

    https://developers.google.com/maps/documentation/places/web-service/reference/rest/v1/places#PriceLevel
    """
    return place.price_level == budget.google_places_price_level


def place_is_accessible(place: places_v1.Place) -> bool:
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
