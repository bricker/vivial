import urllib.parse
import uuid
from collections.abc import Sequence
from textwrap import dedent

from google.maps.places import GetPlaceRequest, Photo, Place, PlacesAsyncClient


from eave.core import database
from eave.core.config import CORE_API_APP_CONFIG
from eave.core.graphql.types.activity import Activity, ActivityTicketInfo, ActivityVenue
from eave.core.graphql.types.location import Location
from eave.core.graphql.types.photos import Photos
from eave.core.graphql.types.restaurant import Restaurant
from eave.core.orm.activity import ActivityOrm
from eave.core.shared.enums import ActivitySource, RestaurantSource
from eave.stdlib.eventbrite.client import EventbriteClient, GetEventQuery
from eave.stdlib.eventbrite.models.event import Event, EventStatus
from eave.stdlib.eventbrite.models.expansions import Expansion
from eave.stdlib.logging import LOGGER

async def activity_from_google_place(*, places_client: PlacesAsyncClient, place: Place) -> Activity:
    photo_uris = await get_google_photo_uris(
        places_client=places_client,
        photos=place.photos,
    )

    return Activity(
        source_id=place.id,
        source=ActivitySource.GOOGLE_PLACES,
        name=place.display_name.text,
        description=place.editorial_summary,
        venue=ActivityVenue(
            name=place.display_name.text,
            location=Location(
                latitude=place.location.latitude,
                longitude=place.location.longitude,
                formatted_address=place.formatted_address,
                directions_uri=place.google_maps_uri,
            ),
        ),
        photos=Photos(
            cover_photo_uri=photo_uris[0] if photo_uris else "",
            supplemental_photo_uris=photo_uris,
        ),
        ticket_info=None, # TODO
        website_uri=place.website_uri,
        door_tips=None,
        insider_tips=None,
        parking_tips=None,
    )

async def activity_from_eventbrite_event(*, eventbrite_client: EventbriteClient, event: Event) -> Activity:
    event_id = event.get("id")

    if not (ticket_availability := event.get("ticket_availability")):
        LOGGER.warning(
            "Missing ticket_availability; excluding event.",
            {"eventbrite_event_id": event_id},
        )
        return

    if not ticket_availability.get("has_available_tickets"):
        LOGGER.warning(
            "has_available_tickets=False; excluding event.",
            {"eventbrite_event_id": event_id},
        )
        return

    if not (event_name := event.get("name")):
        LOGGER.warning(
            "event name missing; excluding event.",
            {"eventbrite_event_id": event_id},
        )
        return

    if event.get("status") != EventStatus.LIVE:
        LOGGER.warning(
            "status != live; excluding event.", {"eventbrite_event_id": event_id}
        )
        return

    if not (venue := event.get("venue")):
        LOGGER.warning(
            "Missing venue; excluding event.", {"eventbrite_event_id": event_id}
        )
        return

    if (venue_address := venue.get("address")) is None:
        LOGGER.warning(
            "Missing venue address; excluding event.",
            {"eventbrite_event_id": event_id},
        )
        return

    if (venue_formatted_address := venue_address.get("localized_address_display")) is None:
        LOGGER.warning(
            "Missing venue localized_address_display; excluding event.",
            {"eventbrite_event_id": event_id},
        )
        return

    if (venue_lat := venue.get("latitude")) is None:
        LOGGER.warning(
            "Missing venue latitude; excluding event.",
            {"eventbrite_event_id": event_id},
        )
        return

    if (venue_lon := venue.get("longitude")) is None:
        LOGGER.warning(
            "Missing venue longitude; excluding event.",
            {"eventbrite_event_id": event_id},
        )
        return

    description = await eventbrite_client.get_event_description(event_id=event_id)
    event["description"] = description

    logo = event.get("logo")

    activity = Activity(
        source_id=event_id,
        source=ActivitySource.EVENTBRITE,
        name=event_name["text"],
        description=event["description"]["text"],
        photos=Photos(
            cover_photo_uri=logo["url"] if logo else None,
            supplemental_photo_uris=None,
        ),
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
        website_uri=event.get("vanity_url"),
        door_tips=None,
        insider_tips=None,
        parking_tips=None,
    )
async def restaurant_from_google_place(*, places_client: PlacesAsyncClient, place: Place) -> Restaurant:
    photo_uris = await get_google_photo_uris(
        places_client=places_client,
        photos=place.photos,
    )

    return Restaurant(
        source_id=place.id,
        source=RestaurantSource.GOOGLE_PLACES,
        location=Location(
            directions_uri=place.google_maps_uri,
            latitude=place.location.latitude,
            longitude=place.location.longitude,
            formatted_address=place.formatted_address,
        ),
        photos=Photos(
            cover_photo_uri=photo_uris[0] if photo_uris else None,
            supplemental_photo_uris=photo_uris,
        ),
        name=place.display_name.text,
        reservable=place.reservable,
        rating=place.rating,
        primary_type_name=place.primary_type_display_name.text,
        website_uri=place.website_uri,
        description=place.editorial_summary,
        parking_tips=None,
        customer_favorites=None,
    )

async def get_google_photo_uris(
    places_client: PlacesAsyncClient,
    photos: Sequence[Photo],
) -> list[str]:
    photo_uris: list[str] = []
    for photo in photos:
        photo_res = await places_client.get_photo_media(
            name=photo.name,
        )
        photo_uris.append(photo_res.photo_uri)
    return photo_uris

async def get_google_place(
    places_client: PlacesAsyncClient,
    id: str,
) -> Place:
    return await places_client.get_place(request=GetPlaceRequest(name=f"places/{id}"))

async def get_eventbrite_activity(*, eventbrite_client: EventbriteClient, event_id: str) -> Activity | None:
    event = await eventbrite_client.get_event_by_id(event_id=event_id)
    activity = await activity_from_eventbrite_event(eventbrite_client=eventbrite_client, event=event)
    return activity

async def get_internal_activity(*, event_id: str) -> Activity | None:
    async with database.async_session.begin() as db_session:
        details = await ActivityOrm.get_one(
            session=db_session,
            id=uuid.UUID(event_id),
        )
    lat, lon = details.coordinates_to_lat_lon()
    formatted_address = dedent(f"""
        {details.address.address1} {details.address.address2}
        {details.address.city}, {details.address.state} {details.address.zip}
        """).strip()

    return Activity(
        source_id=event_id,
        source=ActivitySource.INTERNAL,
        name=details.title,
        description=details.description,
        venue=ActivityVenue(
            name=details.title,
            location=Location(
                latitude=lat,
                longitude=lon,
                formatted_address=formatted_address,
                directions_uri="",
            ),
        ),
        photos=None, # TODO
        ticket_info=None, # TODO
        website_uri=details.booking_url,
        door_tips=None,
        insider_tips=None,
        parking_tips=None,
    )

async def get_google_places_activity(*, places_client: PlacesAsyncClient, event_id: str) -> Activity:
    place = await get_google_place(
        places_client=places_client,
        id=event_id,
        # field_mask=",".join(["displayName.text", "addressComponents", "location", "websiteUri"]),
    )

    activity = await activity_from_google_place(places_client=places_client, place=place)
    return activity

async def get_google_places_restaurant(*, places_client: PlacesAsyncClient, restaurant_id: str) -> Restaurant:
    place = await get_google_place(
        places_client=places_client,
        id=restaurant_id,
        # field_mask=",".join(["displayName.text", "addressComponents", "location", "websiteUri"]),
    )

    restaurant = await restaurant_from_google_place(places_client=places_client, place=place)
    return restaurant

async def get_activity(
    event_source: ActivitySource,
    event_id: str,
) -> Activity | None:
    places_client = PlacesAsyncClient()
    eventbrite_client = EventbriteClient(api_key=CORE_API_APP_CONFIG.eventbrite_api_key)

    match event_source:
        case ActivitySource.INTERNAL:
            activity = await get_internal_activity(event_id=event_id)
            return activity

        case ActivitySource.GOOGLE_PLACES:
            activity = await get_google_places_activity(places_client=places_client, event_id=event_id)
            return activity

        case ActivitySource.EVENTBRITE:
            activity = await get_eventbrite_activity(eventbrite_client=eventbrite_client, event_id=event_id)


async def get_restaurant(
    event_source: RestaurantSource,
    restaurant_id: str,
) -> Restaurant:
    places_client = PlacesAsyncClient()

    match event_source:
        case RestaurantSource.GOOGLE_PLACES:
            restaurant = await get_google_places_restaurant(places_client=places_client, restaurant_id=restaurant_id)
            return restaurant

def google_maps_directions_url(address: str) -> str:
    urlsafe_addr = urllib.parse.quote_plus(address)
    return f"https://www.google.com/maps/place/{urlsafe_addr}"
