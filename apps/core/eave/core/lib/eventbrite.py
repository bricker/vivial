from eave.core.graphql.types.activity import Activity, ActivityVenue
from eave.core.graphql.types.location import Location
from eave.core.graphql.types.photos import Photos
from eave.core.lib.google_places import google_maps_directions_url
from eave.core.shared.enums import ActivitySource
from eave.stdlib.eventbrite.client import EventbriteClient, GetEventQuery, ListTicketClassesForSaleQuery
from eave.stdlib.eventbrite.models.event import Event, EventStatus
from eave.stdlib.eventbrite.models.expansions import Expansion
from eave.stdlib.eventbrite.models.ticket_class import PointOfSale, TicketClass
from eave.stdlib.logging import LOGGER


async def get_eventbrite_activity(eventbrite_client: EventbriteClient, *, event_id: str) -> Activity | None:
    event = await eventbrite_client.get_event_by_id(event_id=event_id, query=GetEventQuery(expand=Expansion.all()))
    activity = await activity_from_eventbrite_event(eventbrite_client=eventbrite_client, event=event)
    return activity


async def activity_from_eventbrite_event(eventbrite_client: EventbriteClient, *, event: Event) -> Activity | None:
    if not (event_id := event.get("id")):
        LOGGER.warning(
            "Missing event_id; excluding event.",
            {"eventbrite_event_id": event_id},
        )
        return

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
        LOGGER.warning("status != live; excluding event.", {"eventbrite_event_id": event_id})
        return

    if not (venue := event.get("venue")):
        LOGGER.warning("Missing venue; excluding event.", {"eventbrite_event_id": event_id})
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

    ticket_classes_paginator = eventbrite_client.list_ticket_classes_for_sale_for_event(
        event_id=event_id,
        query=ListTicketClassesForSaleQuery(
            pos=PointOfSale.ONLINE,
        ),
    )

    best_ticket_class: TicketClass | None = None
    max_cost_cents = 0

    async for batch in ticket_classes_paginator:
        for ticket_class in batch:
            base_cost = ticket_class.get("cost")
            if base_cost is None:
                continue

            total_cost_cents = base_cost["value"]

            if (tax := ticket_class.get("tax")) is not None:
                total_cost_cents += tax["value"]

            if (fee := ticket_class.get("fee")) is not None:
                total_cost_cents += fee["value"]

            if total_cost_cents > max_cost_cents:
                best_ticket_class = ticket_class

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
        ticket_info=ActivityTicketInfo(),
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

    return activity
