import asyncio

from cachetools import TTLCache

from eave.core.config import CORE_API_APP_CONFIG
from eave.core.graphql.types.activity import Activity, ActivityCategoryGroup, ActivityVenue
from eave.core.graphql.types.address import GraphQLAddress
from eave.core.graphql.types.cost_breakdown import CostBreakdown
from eave.core.graphql.types.location import Location
from eave.core.graphql.types.photos import Photo, Photos
from eave.core.graphql.types.ticket_info import TicketInfo
from eave.core.lib.address import format_address
from eave.core.lib.google_places import GooglePlacesUtility
from eave.core.orm.activity_category import ActivityCategoryOrm
from eave.core.orm.activity_category_group import ActivityCategoryGroupOrm
from eave.core.orm.survey import SurveyOrm
from eave.core.shared.enums import ActivitySource, OutingBudget
from eave.core.shared.geo import GeoPoint
from eave.stdlib.eventbrite.client import EventbriteClient, GetEventQuery, ListTicketClassesForSaleQuery
from eave.stdlib.eventbrite.models.event import Event, EventStatus
from eave.stdlib.eventbrite.models.expansions import Expansion
from eave.stdlib.eventbrite.models.ticket_class import PointOfSale, TicketClass
from eave.stdlib.logging import LOGGER
from eave.stdlib.time import ONE_DAY_IN_SECONDS

_EVENTBRITE_EVENT_CACHE = TTLCache[str, Event](maxsize=10**3, ttl=ONE_DAY_IN_SECONDS)


class EventbriteUtility:
    client: EventbriteClient
    _places: GooglePlacesUtility
    _lock: asyncio.Lock

    def __init__(self) -> None:
        self.client = EventbriteClient(api_keys=CORE_API_APP_CONFIG.eventbrite_api_keys)
        self._places = GooglePlacesUtility()
        self._lock = asyncio.Lock()

    async def get_eventbrite_event(self, *, event_id: str) -> Event:
        async with self._lock:
            if event_id in _EVENTBRITE_EVENT_CACHE:
                return _EVENTBRITE_EVENT_CACHE[event_id]

            event = await self.client.get_event_by_id(event_id=event_id, query=GetEventQuery(expand=Expansion.all()))
            _EVENTBRITE_EVENT_CACHE[event_id] = event
            return event

    async def get_eventbrite_activity(self, *, event_id: str, survey: SurveyOrm | None) -> Activity | None:
        event = await self.get_eventbrite_event(event_id=event_id)

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

        ticket_classes_paginator = self.client.list_ticket_classes_for_sale_for_event(
            event_id=event_id,
            query=ListTicketClassesForSaleQuery(
                pos=PointOfSale.ONLINE,
            ),
        )

        # Start with a price with all 0's
        most_expensive_eligible_price = CostBreakdown()
        most_expensive_eligible_ticket_class: TicketClass | None = None

        async for batch in ticket_classes_paginator:
            for ticket_class in batch:
                base_cost = ticket_class.get("cost")
                if base_cost is None:
                    continue

                cost_breakdown = CostBreakdown(base_cost_cents=base_cost["value"])

                if (fee := ticket_class.get("fee")) is not None:
                    cost_breakdown.fee_cents = fee["value"]

                if (tax := ticket_class.get("tax")) is not None:
                    cost_breakdown.tax_cents = tax["value"]

                total_cost_cents = cost_breakdown.calculate_total_cost_cents()
                max_budget = survey.budget if survey else OutingBudget.default()

                # If The total cost is <= the upper bound of the user's selected budget, then it is eligible.
                cost_is_lte_max_budget = (
                    max_budget.upper_limit_cents is None or total_cost_cents <= max_budget.upper_limit_cents
                )

                if (
                    cost_is_lte_max_budget
                    and total_cost_cents > most_expensive_eligible_price.calculate_total_cost_cents()
                ):
                    most_expensive_eligible_price = cost_breakdown
                    most_expensive_eligible_ticket_class = ticket_class

        if event_description := event.get("description"):
            event_description_text = event_description["text"]
        else:
            event_description_text = None

        vivial_activity_category_group = None

        if eventbrite_subcategory_id := event.get("subcategory_id"):
            if vivial_activity_category := ActivityCategoryOrm.get_by_eventbrite_subcategory_id(
                eventbrite_subcategory_id=eventbrite_subcategory_id
            ):
                vivial_activity_category_group = ActivityCategoryGroupOrm.one_or_none(
                    activity_category_group_id=vivial_activity_category.activity_category_group_id
                )

        logo = event.get("logo")

        address = GraphQLAddress(
            address1=venue_address.get("address_1"),
            address2=venue_address.get("address_2"),
            city=venue_address.get("city"),
            state=venue_address.get("region"),
            zip_code=venue_address.get("postal_code"),
            country=venue_address.get("country"),
        )

        photos = Photos(
            cover_photo=Photo(
                id=logo["id"],
                src=logo["url"],
                alt=None,
                attributions=[],
            )
            if logo
            else None,
            supplemental_photos=[],  # Eventbrite only gives one image
        )

        coordinates = GeoPoint(
            lat=float(venue_lat),
            lon=float(venue_lon),
        )

        directions_uri = await self._places.google_maps_directions_url(format_address(address, singleline=True))

        activity = Activity(
            source_id=event_id,
            source=ActivitySource.EVENTBRITE,
            is_bookable=True,  # Eventbrite tickets always bookable
            name=event_name["text"],
            description=event_description_text,
            photos=photos,
            ticket_info=TicketInfo(
                name=most_expensive_eligible_ticket_class.get("display_name"),
                notes=most_expensive_eligible_ticket_class.get(
                    "description"
                ),  # FIXME: This is probably not the info we want for this field.
                cost_breakdown=most_expensive_eligible_price,
            )
            if most_expensive_eligible_ticket_class
            else None,
            venue=ActivityVenue(
                name=venue["name"],
                location=Location(
                    directions_uri=directions_uri,
                    address=address,
                    coordinates=coordinates,
                ),
            ),
            website_uri=event.get("vanity_url") or event.get("url"),
            door_tips=None,
            insider_tips=None,
            parking_tips=None,
            primary_type_name=None,
            category_group=ActivityCategoryGroup.from_orm(vivial_activity_category_group)
            if vivial_activity_category_group
            else None,
        )

        return activity
