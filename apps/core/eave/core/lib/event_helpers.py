from collections.abc import Sequence
from textwrap import dedent
import uuid
from eave.stdlib.eventbrite.client import EventbriteClient, GetEventQuery
from eave.stdlib.eventbrite.models.expansions import Expansion
from google.maps.places_v1 import PlacesAsyncClient, Photo

from eave.core import database
from eave.core.graphql.resolvers.mutations.helpers.planner import get_place
from eave.core.graphql.types.activity import Activity, ActivityTicketInfo, ActivityVenue
from eave.core.graphql.types.location import Location
from eave.core.graphql.types.photos import Photos
from eave.core.graphql.types.restaurant import Restaurant
from eave.core.orm.activity import ActivityOrm
from eave.core.shared.enums import ActivitySource, RestaurantSource


async def _get_google_photo_uris(
    places_client: PlacesAsyncClient,
    photos: Sequence[Photo],
) -> list[str]:
    photo_uris = []
    for photo in photos:
        photo_res = await places_client.get_photo_media(
            name=photo.name,
        )
        photo_uris.append(photo_res.photo_uri)
    return photo_uris


async def get_activity(
    places_client: PlacesAsyncClient,
    activities_client: EventbriteClient,
    event_source: ActivitySource,
    event_id: str,
) -> Activity:
    match event_source:
        case ActivitySource.INTERNAL:
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
                id=event_id,
                source=event_source,
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
                photos=None,
                ticket_info=None,
                website_uri=details.booking_url,
                door_tips=None,
                insider_tips=None,
                parking_tips=None,
            )
        case ActivitySource.GOOGLE_PLACES:
            details = await get_place(
                client=places_client,
                id=event_id,
                # field_mask=",".join(["displayName.text", "addressComponents", "location", "websiteUri"]),
            )

            photo_uris = await _get_google_photo_uris(
                places_client=places_client,
                photos=details.photos,
            )

            return Activity(
                id=event_id,
                source=event_source,
                name=details.display_name.text,
                description="",
                venue=ActivityVenue(
                    name=details.display_name.text,
                    location=Location(
                        latitude=details.location.latitude,
                        longitude=details.location.longitude,
                        formatted_address=details.formatted_address,
                        directions_uri=details.google_maps_uri,
                    ),
                ),
                photos=Photos(
                    cover_photo_uri=photo_uris[0] if photo_uris else "",
                    supplemental_photo_uris=photo_uris,
                ),
                ticket_info=None,
                website_uri=details.website_uri,
                door_tips=None,
                insider_tips=None,
                parking_tips=None,
            )
        case ActivitySource.EVENTBRITE:
            details = await activities_client.get_event_by_id(
                event_id=event_id,
                query=GetEventQuery(expand=[Expansion.VENUE, Expansion.LOGO]),
            )
            name = details.get("name", {}).get("text")
            booking_uri = details.get("url")
            venue = details.get("venue")
            assert venue is not None, "Got no venue info from Eventbrite"
            logo = details.get("logo")
            assert logo is not None, "Got no logo info from Eventbrite"
            lat = float(venue.get("latitude", "0.0"))
            lon = float(venue.get("longitude", "0.0"))
            ven_name = venue.get("name")
            address = venue.get("address") or {}
            formatted_address = address.get("localized_address_display")

            return Activity(
                id=event_id,
                source=event_source,
                name=name or "",
                description=details.get("summary") or "",
                venue=ActivityVenue(
                    name=ven_name,
                    location=Location(
                        latitude=lat,
                        longitude=lon,
                        formatted_address=formatted_address or "",
                        directions_uri="",
                    ),
                ),
                photos=Photos(
                    cover_photo_uri=logo.get("original", {}).get("url") or "",
                    supplemental_photo_uris=None,
                ),
                ticket_info=ActivityTicketInfo(
                    type="",  # TODO: how we get this for the ticket that was actually bought in booking? we store that anywhere?
                    notes="",
                    cost=0,
                    fee=0,
                    tax=0,
                ),
                website_uri=booking_uri,
                door_tips=None,
                insider_tips=None,
                parking_tips=None,
            )


async def get_restuarant(
    places_client: PlacesAsyncClient,
    event_source: RestaurantSource,
    event_id: str,
) -> Restaurant:
    match event_source:
        case RestaurantSource.GOOGLE_PLACES:
            details = await get_place(
                client=places_client,
                id=event_id,
                # field_mask=",".join(["displayName.text", "addressComponents", "location", "websiteUri"]),
            )

            photo_uris = await _get_google_photo_uris(
                places_client=places_client,
                photos=details.photos,
            )

            return Restaurant(
                id=event_id,
                source=event_source,
                location=Location(
                    directions_uri=details.google_maps_uri,
                    latitude=details.location.latitude,
                    longitude=details.location.longitude,
                    formatted_address=details.formatted_address,
                ),
                photos=Photos(
                    cover_photo_uri=photo_uris[0] if photo_uris else "",
                    supplemental_photo_uris=photo_uris,
                ),
                name=details.display_name.text,
                reservable=details.reservable,
                rating=details.rating,
                primary_type_name=details.primary_type_display_name.text,
                website_uri=details.website_uri,
                description="",
                parking_tips=None,
                customer_favorites=None,
            )
