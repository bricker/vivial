import asyncio
import os

from eave.stdlib.eventbrite.client import EventbriteClient, OrderBy
from eave.stdlib.eventbrite.models.event import EventStatus


async def main() -> None:
    client = EventbriteClient(api_key=os.environ["EVENTBRITE_API_KEY"])

    event = await client.get_event_by_id(event_id="1016944647817")
    print("event:", event)
    print()

    if event:
        if organizer_id := event.get("organizer_id"):
            organizer = await client.get_organizer_by_id(organizer_id=organizer_id)
            print("organizer:", organizer)
            print()

            organizer_events = await client.list_events_for_organizer(
                organizer_id=organizer_id, query={"status": EventStatus.LIVE, "order_by": OrderBy.START_ASC}
            )
            print("organizer_events:", organizer_events)
            print()

        if event_id := event.get("id"):
            ticket_classes_for_sale = await client.list_ticket_classes_for_sale_for_event(event_id=event_id)
            print("ticket_classes_for_sale:", ticket_classes_for_sale)
            print()

            default_questions = await client.list_default_questions_for_event(event_id=event_id)
            print("default_questions:", default_questions)
            print()

            custom_questions = await client.list_custom_questions_for_event(event_id=event_id)
            print("custom_questions:", custom_questions)
            print()

    categories = await client.list_categories()
    print("categories:", categories)
    print()

    subcategories = await client.list_subcategories()
    print("subcategories:", subcategories)
    print()

    formats = await client.list_formats()
    print("formats:", formats)
    print()


if __name__ == "__main__":
    asyncio.run(main())
