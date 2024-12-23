import enum
import urllib.parse
from collections.abc import Sequence
from datetime import datetime, timedelta
from functools import lru_cache
from uuid import UUID
from zoneinfo import ZoneInfo

import googlemaps.geocoding
from google.maps.places import (
    GetPhotoMediaRequest,
    GetPlaceRequest,
    Place,
    SearchNearbyRequest,
)
from google.maps.places import (
    Photo as PlacePhoto,
)

from eave.core.graphql.types.activity import Activity, ActivityCategoryGroup, ActivityVenue
from eave.core.graphql.types.address import GraphQLAddress
from eave.core.graphql.types.location import Location
from eave.core.graphql.types.photos import Photo, Photos
from eave.core.graphql.types.restaurant import Restaurant
from eave.core.lib.api_clients import GOOGLE_MAPS_API_CLIENT, GOOGLE_MAPS_PLACES_API_CLIENT
from eave.core.orm.activity_category_group import ActivityCategoryGroupOrm
from eave.core.shared.enums import ActivitySource, RestaurantSource
from eave.core.shared.geo import GeoArea, GeoPoint

# You must pass a field mask to the Google Places API to specify the list of fields to return in the response.
# Reference: https://developers.google.com/maps/documentation/places/web-service/nearby-search
_PLACE_FIELDS = [
    "id",
    "displayName",
    "accessibilityOptions",
    "addressComponents",
    "formattedAddress",
    "businessStatus",
    "googleMapsUri",
    "location",
    "photos",
    "primaryType",
    "primaryTypeDisplayName",
    "types",
    "nationalPhoneNumber",
    "priceLevel",
    "rating",
    "regularOpeningHours",
    "currentOpeningHours",
    "userRatingCount",
    "websiteUri",
    "reservable",
]
_SEARCH_NEARBY_FIELD_MASK = ",".join([f"places.{s}" for s in _PLACE_FIELDS])
_PLACE_FIELD_MASK = ",".join(_PLACE_FIELDS)


async def restaurant_from_google_place(*, place: Place) -> Restaurant:
    photos = await photos_from_google_place(place=place)

    return Restaurant(
        source_id=place.id,
        source=RestaurantSource.GOOGLE_PLACES,
        location=location_from_google_place(place),
        photos=photos,
        name=place.display_name.text,
        reservable=place.reservable,
        rating=place.rating,
        primary_type_name=place.primary_type_display_name.text,
        website_uri=place.website_uri,
        description=place.editorial_summary,
        parking_tips=None,
        customer_favorites=None,
    )


async def activity_from_google_place(*, place: Place) -> Activity:
    photos = await photos_from_google_place(place=place)

    activity = Activity(
        source_id=place.id,
        source=ActivitySource.GOOGLE_PLACES,
        name=place.display_name.text,
        description=place.editorial_summary,
        photos=photos,
        ticket_info=None,  # No tickets for activity from Google Places
        venue=ActivityVenue(name=place.display_name.text, location=location_from_google_place(place)),
        website_uri=place.website_uri,
        door_tips=None,
        insider_tips=None,
        parking_tips=None,
        primary_type_name=place.primary_type_display_name.text,
        category_group=ActivityCategoryGroup.from_orm(
            # NOTE: assumes all google places activities will be a food/drink thing
            ActivityCategoryGroupOrm.one_or_exception(
                activity_category_group_id=UUID("f3a21e9638d2401ebc290fee6fe44384")
            )
        ),
    )

    return activity


async def photos_from_google_place(*, place: Place) -> Photos:
    photos = Photos(cover_photo=None, supplemental_photos=[])

    if len(place.photos) > 0:
        photos.cover_photo = await photo_from_google_place_photo(
            photo=place.photos[0],
        )

    for place_photo in place.photos[1:]:
        supplemental_photo = await photo_from_google_place_photo(
            photo=place_photo,
        )
        photos.supplemental_photos.append(supplemental_photo)

    return photos


class GooglePlaceAddressComponentType(enum.StrEnum):
    administrative_area_level_1 = "administrative_area_level_1"
    country = "country"
    locality = "locality"
    postal_code = "postal_code"
    street_address = "street_address"
    street_number = "street_number"
    route = "route"
    subpremise = "subpremise"


def location_from_google_place(place: Place) -> Location:
    address = GraphQLAddress(
        country=next(
            (
                component.short_text
                for component in place.address_components
                if GooglePlaceAddressComponentType.country.value in component.types
            ),
            None,
        ),
        state=next(
            (
                component.short_text
                for component in place.address_components
                if GooglePlaceAddressComponentType.administrative_area_level_1.value in component.types
            ),
            None,
        ),
        city=next(
            (
                component.long_text
                for component in place.address_components
                if GooglePlaceAddressComponentType.locality.value in component.types
            ),
            "",
        ),
        zip_code=next(
            (
                component.long_text
                for component in place.address_components
                if GooglePlaceAddressComponentType.postal_code.value in component.types
            ),
            None,
        ),
        address1=next(
            (
                component.long_text
                for component in place.address_components
                if GooglePlaceAddressComponentType.street_address.value in component.types
            ),
            None,
        )
        or " ".join(  # fallback to constructing address from more granular components
            [
                next(
                    (
                        component.long_text
                        for component in place.address_components
                        if GooglePlaceAddressComponentType.street_number.value in component.types
                    ),
                    "",
                ),
                next(
                    (
                        component.long_text
                        for component in place.address_components
                        if GooglePlaceAddressComponentType.route.value in component.types
                    ),
                    "",
                ),
            ]
        ),
        address2=next(
            (
                component.long_text
                for component in place.address_components
                if GooglePlaceAddressComponentType.subpremise.value in component.types
            ),
            None,
        ),
    )

    return Location(
        directions_uri=place.google_maps_uri,
        coordinates=GeoPoint(
            lat=place.location.latitude,
            lon=place.location.longitude,
        ),
        address=address,
    )


# Warning: This function cannot be cached, because the photo media response contains temporary, expiring image URLs
async def photo_from_google_place_photo(
    *,
    photo: PlacePhoto,
) -> Photo:
    photo_res = await GOOGLE_MAPS_PLACES_API_CLIENT.get_photo_media(
        request=GetPhotoMediaRequest(
            name=f"{photo.name}/media",
            max_width_px=1000,  # This value was chosen arbitrarily
        )
    )

    return Photo(
        id=photo_res.name,
        src=photo_res.photo_uri,
        alt=None,
        attributions=[attribution.display_name for attribution in photo.author_attributions]
        if photo.author_attributions
        else [],
    )


async def get_google_place(
    *,
    place_id: str,
) -> Place:
    return await _cached_get_google_place(place_id=place_id)


@lru_cache(maxsize=100)
async def _cached_get_google_place(*, place_id: str) -> Place:
    # This is its own function because lru_cache breaks function intellisense
    return await GOOGLE_MAPS_PLACES_API_CLIENT.get_place(
        request=GetPlaceRequest(name=f"places/{place_id}"), metadata=[("x-goog-fieldmask", _PLACE_FIELD_MASK)]
    )


async def get_google_places_activity(*, event_id: str) -> Activity | None:
    place = await get_google_place(
        place_id=event_id,
    )

    activity = await activity_from_google_place(place=place)
    return activity


async def get_google_places_restaurant(*, restaurant_id: str) -> Restaurant:
    place = await get_google_place(
        place_id=restaurant_id,
    )

    restaurant = await restaurant_from_google_place(place=place)
    return restaurant


async def get_places_nearby(
    *,
    area: GeoArea,
    included_primary_types: Sequence[str],
) -> list[Place]:
    """
    Given a Google Places API client, use it to search for places nearby the
    given latitude and longitude that meet the given constraints.

    https://developers.google.com/maps/documentation/places/web-service/nearby-search
    """

    return await _cached_get_places_nearby(
        center_lat=area.center.lat,
        center_lon=area.center.lon,
        rad_meters=area.rad.meters,
        included_primary_types=included_primary_types,
    )


@lru_cache(maxsize=100)
async def _cached_get_places_nearby(
    *,
    center_lat: float,
    center_lon: float,
    rad_meters: float,
    included_primary_types: Sequence[str],
) -> list[Place]:
    location_restriction = SearchNearbyRequest.LocationRestriction()
    location_restriction.circle.radius = rad_meters
    location_restriction.circle.center.latitude = center_lat
    location_restriction.circle.center.longitude = center_lon
    request = SearchNearbyRequest(
        location_restriction=location_restriction,
        included_primary_types=included_primary_types[0:50],
    )
    response = await GOOGLE_MAPS_PLACES_API_CLIENT.search_nearby(
        request=request, metadata=[("x-goog-fieldmask", _SEARCH_NEARBY_FIELD_MASK)]
    )
    return list(response.places)


def place_will_be_open(*, place: Place, arrival_time: datetime, departure_time: datetime, timezone: ZoneInfo) -> bool:
    """
    Given a place from the Google Places API, determine whether or not that
    place will be open during the given time period.

    https://developers.google.com/maps/documentation/places/web-service/reference/rest/v1/places#OpeningHours
    """
    arrival_time_local = arrival_time.astimezone(timezone)
    departure_time_local = departure_time.astimezone(timezone)

    for period in place.regular_opening_hours.periods:
        is_relevant = period.open_.day == arrival_time_local.weekday()

        if is_relevant:
            open_time = arrival_time_local.replace(hour=period.open_.hour, minute=period.open_.minute)
            close_time = arrival_time_local.replace(hour=period.close.hour, minute=period.close.minute)

            if period.close.day != arrival_time_local.weekday():
                close_time = close_time + timedelta(days=1)  # Place closes the next day.

            if open_time <= arrival_time_local and close_time >= departure_time_local:
                return True

    return False


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


async def google_maps_directions_url(address: str) -> str:
    return await _cached_google_maps_directions_url(address)


@lru_cache(maxsize=500)
async def _cached_google_maps_directions_url(address: str) -> str:
    geocode_result = googlemaps.geocoding.geocode(client=GOOGLE_MAPS_API_CLIENT, address=address)

    if place_id := geocode_result.get("place_id"):
        place = await get_google_place(place_id=place_id)
        if place.google_maps_uri:
            return place.google_maps_uri

    urlsafe_addr = urllib.parse.quote_plus(address)
    return f"https://www.google.com/maps/place/{urlsafe_addr}"
