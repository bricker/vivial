import urllib.parse
from collections.abc import MutableSequence, Sequence
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from google.maps.places import (
    GetPhotoMediaRequest,
    GetPlaceRequest,
    Photo as PlacePhoto,
    Place,
    PlacesAsyncClient,
    SearchNearbyRequest,
)

from eave.core.graphql.types.activity import Activity, ActivityVenue
from eave.core.graphql.types.location import Location
from eave.core.graphql.types.photos import Photo, Photos
from eave.core.graphql.types.pricing import Pricing
from eave.core.graphql.types.restaurant import Restaurant
from eave.core.shared.address import Address
from eave.core.shared.enums import ActivitySource, OutingBudget, RestaurantSource
from eave.core.shared.geo import GeoArea, GeoPoint

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


async def restaurant_from_google_place(places_client: PlacesAsyncClient, *, place: Place) -> Restaurant:
    photos = await photos_from_google_place(places_client, place=place)

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


async def activity_from_google_place(places_client: PlacesAsyncClient, *, place: Place) -> Activity:
    photos = await photos_from_google_place(places_client, place=place)

    activity = Activity(
        source_id=place.id,
        source=ActivitySource.GOOGLE_PLACES,
        name=place.display_name.text,
        description=place.editorial_summary,
        photos=photos,
        pricing=Pricing(),  # Currently activities from Google Places (ice cream shop or bar) don't have pricing (i.e., we don't collect payment)
        venue=ActivityVenue(name=place.display_name.text, location=location_from_google_place(place)),
        website_uri=place.website_uri,
        door_tips=None,
        insider_tips=None,
        parking_tips=None,
    )

    return activity


async def photos_from_google_place(places_client: PlacesAsyncClient, *, place: Place) -> Photos:
    photos = Photos(cover_photo=None, supplemental_photos=[])

    if len(place.photos) > 0:
        photos.cover_photo = await photo_from_google_place_photo(
            places_client=places_client,
            photo=place.photos[0],
        )

    for place_photo in place.photos[1:]:
        supplemental_photo = await photo_from_google_place_photo(
            places_client=places_client,
            photo=place_photo,
        )
        photos.supplemental_photos.append(supplemental_photo)

    return photos


def location_from_google_place(place: Place) -> Location:
    # FIXME
    for component in place.address_components:
        if "abc" in component.types:
            pass

    return Location(
        directions_uri=place.google_maps_uri,
        coordinates=GeoPoint(
            lat=place.location.latitude,
            lon=place.location.longitude,
        ),
        address=Address(
            address1=place.formatted_address, # This is a hack
            address2=None,
            city=None,
            state=None,
            zip=None,
            country=None,
        ),
    )


async def photo_from_google_place_photo(
    places_client: PlacesAsyncClient,
    *,
    photo: PlacePhoto,
) -> Photo:
    photo_res = await places_client.get_photo_media(
        request=GetPhotoMediaRequest(
            name=f"{photo.name}/media",
            max_width_px=1000,  # This value was chosen arbitrarily
        )
    )

    return Photo(
        id=photo_res.name,
        src=photo_res.photo_uri,
        alt=None,
        attributions=[attribution.display_name for attribution in photo.author_attributions],
    )


async def get_google_place(
    places_client: PlacesAsyncClient,
    *,
    place_id: str,
) -> Place:
    return await places_client.get_place(request=GetPlaceRequest(name=f"places/{place_id}"))


async def get_google_places_activity(places_client: PlacesAsyncClient, *, event_id: str) -> Activity | None:
    place = await get_google_place(
        places_client=places_client,
        place_id=event_id,
    )

    activity = await activity_from_google_place(places_client, place=place)
    return activity


async def get_google_places_restaurant(places_client: PlacesAsyncClient, *, restaurant_id: str) -> Restaurant:
    place = await get_google_place(
        places_client=places_client,
        place_id=restaurant_id,
    )

    restaurant = await restaurant_from_google_place(places_client=places_client, place=place)
    return restaurant


async def get_places_nearby(
    places_client: PlacesAsyncClient,
    *,
    area: GeoArea,
    included_primary_types: Sequence[str],
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
    response = await places_client.search_nearby(
        request=request, metadata=[("x-goog-fieldmask", _RESTAURANT_FIELD_MASK)]
    )
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
