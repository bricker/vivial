import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo

import eave.core.internal.database
from eave.core.internal.config import CORE_API_APP_CONFIG
from eave.core.orm.eventbrite_event import EventbriteEventOrm
from eave.core.outing.constants.activities import get_vivial_subcategory_by_eventbrite_subcategory_id
from eave.core.outing.constants.formats import get_vivial_format_from_eventbrite_format_id
from eave.stdlib.eventbrite.client import EventbriteClient, ListEventsQuery, OrderBy
from eave.stdlib.eventbrite.models.event import EventStatus
from eave.stdlib.eventbrite.models.expansions import Expansion
from eave.stdlib.logging import LOGGER

# These are hand-picked by Vivial staff
_EVENTBRITE_ORGANIZER_IDS = [
    "46435628873",  # https://www.eventbrite.com/o/vip-46435628873
    "8155301277",  # https://www.eventbrite.com/o/supreme-hollywood-group-8155301277
]


async def get_eventbrite_events() -> None:
    client = EventbriteClient(api_key=CORE_API_APP_CONFIG.eventbrite_api_key)

    for organizer_id in _EVENTBRITE_ORGANIZER_IDS:
        paginator = client.list_events_for_organizer(
            organizer_id=organizer_id,
            query=ListEventsQuery(
                order_by=OrderBy.START_ASC,
                status=EventStatus.LIVE,
                only_public=True,
                expand=[
                    Expansion.TICKET_AVAILABILITY,
                    Expansion.CATEGORY,
                    Expansion.SUBCATEGORY,
                    Expansion.FORMAT,
                    Expansion.VENUE,
                ],
            ),
        )

        pagenum = 0
        async for batch in paginator:
            pagenum += 1
            LOGGER.debug(f"organizer {organizer_id}; pagenum {pagenum}")

            async with eave.core.internal.database.async_session.begin() as db_session:
                evnum = 0
                for event in batch:
                    evnum += 1
                    # FIXME: This will ignore events that may have previously been added into the database, if their settings were changed to become excluded.

                    if (eventbrite_event_id := event.get("id")) is None:
                        LOGGER.warning("No eventbrite event id; skipping")
                        continue

                    pfx = f"[{evnum}/{len(batch)}; {eventbrite_event_id}]"
                    LOGGER.debug(f"{pfx} processing event", {"eventbrite_organizer_id": organizer_id})

                    if event.get("online_event") is True:
                        LOGGER.debug(f"{pfx} online_event=True; skipping", {"eventbrite_event_id": eventbrite_event_id})
                        continue

                    if event.get("is_locked") is True:
                        LOGGER.debug(f"{pfx} is_locked=True; skipping", {"eventbrite_event_id": eventbrite_event_id})
                        continue

                    if event.get("show_pick_a_seat") is True:
                        LOGGER.debug(
                            f"{pfx} show_pick_a_seat=True skipping", {"eventbrite_event_id": eventbrite_event_id}
                        )
                        continue

                    if event.get("is_sold_out") is True:
                        LOGGER.debug(f"{pfx} is_sold_out=True; skipping", {"eventbrite_event_id": eventbrite_event_id})
                        continue

                    if event.get("category_id") is None:
                        LOGGER.debug(f"{pfx} category_id=None; skipping", {"eventbrite_event_id": eventbrite_event_id})
                        continue

                    if (eb_subcategory_id := event.get("subcategory_id")) is None:
                        LOGGER.debug(
                            f"{pfx} subcategory_id=None; skipping", {"eventbrite_event_id": eventbrite_event_id}
                        )
                        continue

                    if (eb_format_id := event.get("format_id")) is None:
                        LOGGER.debug(f"{pfx} format_id=None; skipping", {"eventbrite_event_id": eventbrite_event_id})
                        continue

                    if not (event_name := event.get("name")):
                        LOGGER.warning(
                            f"{pfx} No eventbrite event name; skipping", {"eventbrite_event_id": eventbrite_event_id}
                        )
                        continue
                    if (venue := event.get("venue")) is None:
                        LOGGER.warning(
                            f"{pfx} No eventbrite event venue; skipping", {"eventbrite_event_id": eventbrite_event_id}
                        )
                        continue
                    if (lat := venue.get("latitude")) is None:
                        LOGGER.warning(
                            f"{pfx} No venue latitude; skipping", {"eventbrite_event_id": eventbrite_event_id}
                        )
                        continue
                    if (lon := venue.get("longitude")) is None:
                        LOGGER.warning(
                            f"{pfx} No venue longitude; skipping", {"eventbrite_event_id": eventbrite_event_id}
                        )
                        continue
                    if (ticket_availability := event.get("ticket_availability")) is None:
                        LOGGER.warning(
                            f"{pfx} No eventbrite ticket_availability; skipping",
                            {"eventbrite_event_id": eventbrite_event_id},
                        )
                        continue

                    if not (
                        vivial_subcategory := get_vivial_subcategory_by_eventbrite_subcategory_id(eb_subcategory_id)
                    ):
                        LOGGER.warning(
                            f"{pfx} No mapped vivial category; skipping", {"eventbrite_event_id": eventbrite_event_id}
                        )
                        continue

                    if not (vivial_format := get_vivial_format_from_eventbrite_format_id(eb_format_id)):
                        LOGGER.warning(
                            f"{pfx} No mapped vivial format; skipping", {"eventbrite_event_id": eventbrite_event_id}
                        )
                        continue

                    if minimum_ticket_price := ticket_availability.get("minimum_ticket_price"):
                        min_cost_cents = minimum_ticket_price["value"]
                    else:
                        min_cost_cents = None

                    if maximum_ticket_price := ticket_availability.get("maximum_ticket_price"):
                        max_cost_cents = maximum_ticket_price["value"]
                    else:
                        max_cost_cents = None

                    if event_start := event.get("start"):
                        start_time = datetime.fromisoformat(event_start["local"]).replace(
                            tzinfo=ZoneInfo(event_start["timezone"])
                        )
                    else:
                        start_time = None

                    if event_end := event.get("end"):
                        end_time = datetime.fromisoformat(event_end["local"]).replace(
                            tzinfo=ZoneInfo(event_end["timezone"])
                        )
                    else:
                        end_time = None

                    query = EventbriteEventOrm.select(
                        eventbrite_event_id=eventbrite_event_id,
                    ).limit(1)

                    target = (await db_session.scalars(query)).one_or_none()
                    if not target:
                        LOGGER.debug(
                            f"{pfx} new event - adding to database", {"eventbrite_event_id": eventbrite_event_id}
                        )
                        target = EventbriteEventOrm(eventbrite_event_id=eventbrite_event_id)
                        db_session.add(target)
                    else:
                        LOGGER.debug(
                            f"{pfx} existing event - updating database", {"eventbrite_event_id": eventbrite_event_id}
                        )

                    target.update(
                        title=event_name["text"],
                        start_time=start_time,
                        end_time=end_time,
                        min_cost_cents=min_cost_cents,
                        max_cost_cents=max_cost_cents,
                        lat=float(lat),
                        lon=float(lon),
                        subcategory_id=vivial_subcategory.id,
                        format_id=vivial_format.id,
                    )


if __name__ == "__main__":
    asyncio.run(get_eventbrite_events())
