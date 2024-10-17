import os

from eave.stdlib.eventbrite.client import EventbriteClient, OrderBy
from eave.stdlib.eventbrite.models.event import EventStatus
from eave.stdlib.eventbrite.models.expansions import Expansion


async def get_eventbrite_events() -> None:
    client = EventbriteClient(api_key=os.environ["EVENTBRITE_API_KEY"])
    organizer_ids = ["88911120483"]

    for organizer_id in organizer_ids:
        events = await client.list_events_for_organizer(
            organizer_id=organizer_id,
            query={
                "order_by": OrderBy.start_asc,
                "status": EventStatus.live,
                "expand": ",".join(
                    [
                        Expansion.ticket_availability,
                        Expansion.category,
                        Expansion.subcategory,
                        Expansion.event_sales_status,
                        Expansion.music_properties,
                        Expansion.venue,
                    ]
                ),
            },
        )

        # store event deltas in database
        print(events)
