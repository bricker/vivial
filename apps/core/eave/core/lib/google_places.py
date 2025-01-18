import enum
import json
import urllib.parse
from collections.abc import MutableSequence, Sequence
from datetime import datetime, timedelta
from typing import ClassVar, TypedDict
from uuid import UUID
from zoneinfo import ZoneInfo

import googlemaps.geocoding
from google.maps.places import (
    GetPhotoMediaRequest,
    GetPlaceRequest,
    PhotoMedia,
    Place,
    PlacesAsyncClient,
    PriceLevel,
    SearchNearbyRequest,
    SearchNearbyResponse,
)
from google.maps.places import (
    Photo as PlacePhoto,
)
from google.maps.routing import ComputeRoutesRequest, ComputeRoutesResponse, RoutesAsyncClient
from google.type import latlng_pb2, localized_text_pb2

from eave.core.config import CORE_API_APP_CONFIG
from eave.core.graphql.context import LogContext
from eave.core.graphql.types.activity import Activity, ActivityCategoryGroup, ActivityVenue
from eave.core.graphql.types.address import GraphQLAddress
from eave.core.graphql.types.location import Location
from eave.core.graphql.types.photos import Photo, Photos
from eave.core.graphql.types.restaurant import Restaurant
from eave.core.orm.activity_category_group import ActivityCategoryGroupOrm
from eave.core.redis import CACHE
from eave.core.shared.enums import ActivitySource, RestaurantSource
from eave.core.shared.geo import GeoArea, GeoPoint
from eave.stdlib.exceptions import suppress_in_production
from eave.stdlib.logging import LOGGER
from eave.stdlib.time import ONE_DAY_IN_SECONDS, ONE_HOUR_IN_SECONDS
from eave.stdlib.util import b64encode

FIELDMASK_HEADER = "x-goog-fieldmask"


class PartialPlace:
    FIELD_MASK: ClassVar[str] = ",".join(
        [
            "id",
            "name",
            "displayName",
            "editorialSummary",
            "generativeSummary",
            "primaryTypeDisplayName",
            "location",
            "addressComponents",
            "googleMapsUri",
            "photos",
            "rating",
            "websiteUri",
            "reservable",
        ]
    )

    _original: Place

    def __init__(self, place: Place) -> None:
        self._original = place

    @property
    def id(self) -> str:
        return self._original.id

    @property
    def name(self) -> str:
        return self._original.name

    @property
    def display_name(self) -> localized_text_pb2.LocalizedText:  # type: ignore
        return self._original.display_name

    @property
    def editorial_summary(self) -> localized_text_pb2.LocalizedText:  # type: ignore
        return self._original.editorial_summary

    @property
    def generative_summary(self) -> Place.GenerativeSummary:
        return self._original.generative_summary

    @property
    def primary_type_display_name(self) -> localized_text_pb2.LocalizedText:  # type: ignore
        return self._original.primary_type_display_name

    @property
    def location(self) -> latlng_pb2.LatLng:  # type:ignore
        return self._original.location

    @property
    def address_components(self) -> MutableSequence[Place.AddressComponent]:
        return self._original.address_components

    @property
    def google_maps_uri(self) -> str:
        return self._original.google_maps_uri

    @property
    def photos(self) -> MutableSequence[PlacePhoto]:
        return self._original.photos

    @property
    def rating(self) -> float:
        return self._original.rating

    @property
    def website_uri(self) -> str:
        return self._original.website_uri

    @property
    def reservable(self) -> bool:
        return self._original.reservable


class SearchNearbyPartialPlace:
    FIELD_MASK: ClassVar[str] = ",".join(
        [
            "places.id",
            "places.businessStatus",
            "places.priceLevel",
            "places.regularOpeningHours",
        ]
    )

    _original: Place

    def __init__(self, place: Place) -> None:
        self._original = place

    @property
    def id(self) -> str:
        return self._original.id

    @property
    def business_status(self) -> Place.BusinessStatus:
        return self._original.business_status

    @property
    def price_level(self) -> PriceLevel:
        return self._original.price_level

    @property
    def regular_opening_hours(self) -> Place.OpeningHours:
        return self._original.regular_opening_hours


class GeocodeLocation(TypedDict, total=False):
    lat: float
    lng: float


class GeocodeGeometry(TypedDict, total=False):
    location: GeocodeLocation


class GeocodeResult(TypedDict, total=False):
    place_id: str | None
    geometry: GeocodeGeometry


class GooglePlaceAddressComponentType(enum.StrEnum):
    administrative_area_level_1 = "administrative_area_level_1"
    country = "country"
    locality = "locality"
    postal_code = "postal_code"
    street_address = "street_address"
    street_number = "street_number"
    route = "route"
    subpremise = "subpremise"


class GoogleMapsUtility:
    _client: googlemaps.Client

    def __init__(self) -> None:
        self._client = googlemaps.Client(key=CORE_API_APP_CONFIG.google_maps_api_key)

    async def geocode(self, address: str) -> list[GeocodeResult]:
        # We can't use hashing here because of hash collisions
        cache_key = f"google_maps:geocode:{b64encode(address)}"

        with suppress_in_production(Exception):
            # TODO: Implement distributed locking (eg via Redlock)
            if cv := await CACHE.get(cache_key):
                LOGGER.debug("CACHE HIT: Google Maps Geocode", {"address": address})
                return json.loads(cv)
            else:
                LOGGER.debug("CACHE MISS: Google Maps Geocode", {"address": address})

        if CORE_API_APP_CONFIG.google_maps_apis_disabled:
            return []

        results: list[GeocodeResult] = googlemaps.geocoding.geocode(client=self._client, address=address)

        with suppress_in_production(Exception):
            await CACHE.set(cache_key, json.dumps(results), ex=ONE_DAY_IN_SECONDS * 7)

        return results


class GoogleRoutesUtility:
    _client: RoutesAsyncClient

    def __init__(self) -> None:
        self._client = RoutesAsyncClient()

    async def compute_routes(
        self,
        *,
        request: ComputeRoutesRequest,
        metadata: list[tuple[str, str | bytes]],
        ctx: LogContext,
    ) -> ComputeRoutesResponse | None:
        _fingerprint = ComputeRoutesRequest.to_json(request, indent=0, sort_keys=True)
        cache_key = f"google_maps:routing:{b64encode(_fingerprint)}"

        with suppress_in_production(Exception, ctx=ctx):
            # TODO: Implement distributed locking (eg via Redlock)
            if cv := await CACHE.get(cache_key):
                LOGGER.debug("CACHE HIT: Google Routing Compute Routes", {"request": _fingerprint})
                cached_response = ComputeRoutesResponse.deserialize(cv)
                if not isinstance(cached_response, ComputeRoutesResponse):
                    raise TypeError(
                        f"expected deserialized object to be a ComputeRoutesResponse, but got a {type(cached_response)}"
                    )
                return cached_response
            else:
                LOGGER.debug("CACHE MISS: Google Routing Compute Routes", {"request": _fingerprint})

        if CORE_API_APP_CONFIG.google_maps_apis_disabled:
            return None

        response = await self._client.compute_routes(request=request, metadata=metadata)

        with suppress_in_production(Exception, ctx=ctx):
            await CACHE.set(cache_key, ComputeRoutesResponse.serialize(response), ex=ONE_HOUR_IN_SECONDS * 24)

        return response


class GooglePlacesUtility:
    _client: PlacesAsyncClient
    _maps: GoogleMapsUtility

    def __init__(self) -> None:
        self._client = PlacesAsyncClient()
        self._maps = GoogleMapsUtility()

    async def get_google_places_activity(self, *, event_id: str) -> Activity | None:
        place = await self.get_google_place(
            place_id=event_id,
        )

        if not place:
            return None

        activity = await self.activity_from_google_place(place)
        return activity

    async def get_google_places_restaurant(self, *, restaurant_id: str) -> Restaurant | None:
        place = await self.get_google_place(
            place_id=restaurant_id,
        )

        if not place:
            return None

        restaurant = await self.restaurant_from_google_place(place)
        return restaurant

    async def restaurant_from_google_place(self, place: PartialPlace) -> Restaurant:
        photos = await self.photos_from_google_place(place)

        return Restaurant(
            source_id=place.id,
            source=RestaurantSource.GOOGLE_PLACES,
            location=self.location_from_google_place(place),
            photos=photos,
            name=place.display_name.text,
            reservable=place.reservable,
            rating=place.rating,
            primary_type_name=place.primary_type_display_name.text,
            website_uri=place.website_uri,
            description=place.editorial_summary.text or place.generative_summary.overview.text,
            parking_tips=None,
            customer_favorites=None,
        )

    async def activity_from_google_place(self, place: PartialPlace) -> Activity:
        photos = await self.photos_from_google_place(place=place)

        activity = Activity(
            source_id=place.id,
            source=ActivitySource.GOOGLE_PLACES,
            is_bookable=False,  # For now, any activity from Google Places is treated as non-bookable.
            name=place.display_name.text,
            description=place.editorial_summary.text or place.generative_summary.overview.text,
            photos=photos,
            ticket_info=None,  # No tickets for activity from Google Places
            venue=ActivityVenue(name=place.display_name.text, location=self.location_from_google_place(place)),
            website_uri=place.website_uri,
            door_tips=None,
            insider_tips=None,
            parking_tips=None,
            primary_type_name=place.primary_type_display_name,
            category_group=ActivityCategoryGroup.from_orm(
                # NOTE: assumes all google places activities will be a food/drink thing
                ActivityCategoryGroupOrm.one_or_exception(
                    activity_category_group_id=UUID("f3a21e9638d2401ebc290fee6fe44384")
                )
            ),
        )

        return activity

    async def photos_from_google_place(self, place: PartialPlace) -> Photos:
        photos = Photos(cover_photo=None, supplemental_photos=[])

        # We catch these requests because if the photos can't be fetched, we should still show the Place result.
        if len(place.photos) > 0:
            with suppress_in_production(Exception):
                photos.cover_photo = await self.photo_from_google_place_photo(
                    place.photos[0],
                )

        # Get up to 2 more photos. This is purely a cost-saving measure. Every call to the Photos API costs money and a Place can return up to 10 photos.
        for place_photo in place.photos[1:3]:
            with suppress_in_production(Exception):
                supplemental_photo = await self.photo_from_google_place_photo(
                    place_photo,
                )
                if supplemental_photo:
                    photos.supplemental_photos.append(supplemental_photo)

        return photos

    async def photo_from_google_place_photo(
        self,
        photo: PlacePhoto,
    ) -> Photo | None:
        cache_key = f"google_maps:places:photo_media:{photo.name}"

        with suppress_in_production(Exception):
            # TODO: Implement distributed locking (eg via Redlock)
            if cv := await CACHE.get(cache_key):
                LOGGER.debug("CACHE HIT: Google Place Photo Media", {"photo": photo})
                cached_photo_media = PhotoMedia.deserialize(cv)
                if not isinstance(cached_photo_media, PhotoMedia):
                    raise TypeError(
                        f"expected deserialized object to be a PhotoMedia, but got a {type(cached_photo_media)}"
                    )
                return self.photo_media_to_photo(photo=photo, photo_media=cached_photo_media)
            else:
                LOGGER.debug("CACHE MISS: Google Place Photo Media", {"photo": photo})

        if CORE_API_APP_CONFIG.google_maps_apis_disabled:
            return None

        photo_media: PhotoMedia | None = None

        with suppress_in_production(Exception):
            photo_media = await self._client.get_photo_media(
                request=GetPhotoMediaRequest(
                    name=f"{photo.name}/media",
                    max_width_px=1000,  # This value was chosen arbitrarily
                ),
            )

        if not photo_media:
            return None

        with suppress_in_production(Exception):
            # FIXME: Place data shouldn't be cached, because 1) the photo names are temporary, and 2) it violates Google's TOS
            await CACHE.set(cache_key, PhotoMedia.serialize(photo_media), ex=ONE_HOUR_IN_SECONDS * 24)

        return self.photo_media_to_photo(photo=photo, photo_media=photo_media)

    def photo_media_to_photo(self, *, photo: PlacePhoto, photo_media: PhotoMedia) -> Photo:
        return Photo(
            id=photo_media.name,
            src=photo_media.photo_uri,
            alt=None,
            attributions=[attribution.display_name for attribution in photo.author_attributions]
            if photo.author_attributions
            else [],
        )

    async def get_google_place(
        self,
        place_id: str,
    ) -> PartialPlace | None:
        cache_key = f"google_maps:places:place:{place_id}"

        with suppress_in_production(Exception):
            # TODO: Implement distributed locking (eg via Redlock)
            if cv := await CACHE.get(cache_key):
                LOGGER.debug("CACHE HIT: Google Place", {"place_id": place_id})
                cached_place = Place.deserialize(cv)
                if not isinstance(cached_place, Place):
                    raise TypeError(f"expected deserialized object to be a Place, but got a {type(cached_place)}")
                return PartialPlace(cached_place)
            else:
                LOGGER.debug("CACHE MISS: Google Place", {"place_id": place_id})

        if CORE_API_APP_CONFIG.google_maps_apis_disabled:
            return None

        place: Place | None = None
        with suppress_in_production(Exception):
            place = await self._client.get_place(
                request=GetPlaceRequest(name=f"places/{place_id}"),
                metadata=[(FIELDMASK_HEADER, PartialPlace.FIELD_MASK)],
            )

        if not place:
            return None

        with suppress_in_production(Exception):
            # FIXME: Place data shouldn't be cached, because 1) the photo names are temporary, and 2) it violates Google's TOS
            await CACHE.set(cache_key, Place.serialize(place), ex=ONE_HOUR_IN_SECONDS * 24)

        return PartialPlace(place)

    async def get_places_nearby(
        self,
        *,
        area: GeoArea,
        included_primary_types: Sequence[str],
    ) -> list[SearchNearbyPartialPlace]:
        """
        Given a Google Places API client, use it to search for places nearby the
        given latitude and longitude that meet the given constraints.

        https://developers.google.com/maps/documentation/places/web-service/nearby-search
        """

        cache_key = f"google_maps:places:search_nearby:{b64encode(area.fingerprint)}:{b64encode(json.dumps(included_primary_types))}"

        with suppress_in_production(Exception):
            # TODO: Implement distributed locking (eg via Redlock)
            if cv := await CACHE.get(cache_key):
                LOGGER.debug(
                    "CACHE HIT: Google Place Search Nearby",
                    {"area": area, "included_primary_types": included_primary_types},
                )
                cached_response = SearchNearbyResponse.deserialize(cv)
                if not isinstance(cached_response, SearchNearbyResponse):
                    raise TypeError(
                        f"expected deserialized object to be a SearchNearbyResponse, but got a {type(cached_response)}"
                    )
                return [SearchNearbyPartialPlace(place) for place in cached_response.places]
            else:
                LOGGER.debug(
                    "CACHE MISS: Google Place Search Nearby",
                    {"area": area, "included_primary_types": included_primary_types},
                )

        if CORE_API_APP_CONFIG.google_maps_apis_disabled:
            return []

        location_restriction = SearchNearbyRequest.LocationRestriction()
        location_restriction.circle.radius = area.rad.meters
        location_restriction.circle.center.latitude = area.center.lat
        location_restriction.circle.center.longitude = area.center.lon
        request = SearchNearbyRequest(
            location_restriction=location_restriction,
            included_primary_types=included_primary_types[0:50], # Maximum 50 types are allowed
            max_result_count=20, # max allowed
        )

        response = await self._client.search_nearby(
            request=request, metadata=[(FIELDMASK_HEADER, SearchNearbyPartialPlace.FIELD_MASK)]
        )

        with suppress_in_production(Exception):
            # FIXME: Place data shouldn't be cached, because 1) the photo names are temporary, and 2) it violates Google's TOS
            await CACHE.set(cache_key, SearchNearbyResponse.serialize(response), ex=ONE_HOUR_IN_SECONDS * 24)

        return [SearchNearbyPartialPlace(place) for place in response.places]

    async def google_maps_directions_url(self, address: str) -> str:
        # Note: Although the lower-level API calls are also cached, We cache the directions URL up-front because that
        # info basically never changes, so we can continue to show the cached values even if we have to disable calls
        # to the Google Maps APIs.

        # We can't use hashing here because of hash collisions
        cache_key = f"google_maps:directions_url:{b64encode(address)}"

        with suppress_in_production(Exception):
            # TODO: Implement distributed locking (eg via Redlock)
            if cv := await CACHE.get(cache_key):
                LOGGER.debug("CACHE HIT: Google Maps Directions URI", {"address": address})
                return str(cv)
            else:
                LOGGER.debug("CACHE MISS: Google Maps Directions URI", {"address": address})

        url: str | None = None

        if not CORE_API_APP_CONFIG.google_maps_apis_disabled:
            with suppress_in_production(Exception):
                geocode_results = await self._maps.geocode(address=address)

                for result in geocode_results:
                    if place_id := result.get("place_id"):
                        place = await self.get_google_place(place_id)
                        if place and place.google_maps_uri:
                            url = place.google_maps_uri

        if not url:
            urlsafe_addr = urllib.parse.quote_plus(address)
            url = f"https://www.google.com/maps/place/{urlsafe_addr}"

        with suppress_in_production(Exception):
            await CACHE.set(cache_key, url, ex=ONE_DAY_IN_SECONDS * 7)

        return url

    def location_from_google_place(self, place: PartialPlace) -> Location:
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

    def place_will_be_open(
        self, *, place: SearchNearbyPartialPlace, arrival_time: datetime, departure_time: datetime, timezone: ZoneInfo
    ) -> bool:
        """
        Given a place from the Google Places API, determine whether or not that
        place will be open during the given time period.

        https://developers.google.com/maps/documentation/places/web-service/reference/rest/v1/places#OpeningHours
        """

        if not place.business_status == Place.BusinessStatus.OPERATIONAL:
            return False

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
