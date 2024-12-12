from datetime import datetime
from uuid import UUID, uuid4

import strawberry

from eave.core import database
from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.types.activity import Activity, ActivityTicketInfo, ActivityVenue
from eave.core.graphql.types.location import Location
from eave.core.graphql.types.outing import (
    Outing,
)
from eave.core.graphql.types.photos import Photos
from eave.core.graphql.types.restaurant import Restaurant
from eave.core.lib.event_helpers import get_activity, get_restaurant
from eave.core.orm.outing_activity import OutingActivityOrm
from eave.core.orm.outing_reservation import OutingReservationOrm
from eave.core.shared.enums import ActivitySource, RestaurantSource
from eave.stdlib.time import LOS_ANGELES_TIMEZONE

# TODO: Remove once Date Picked UI is complete.
MOCK_OUTING = Outing(
    id=uuid4(),
    headcount=2,
    driving_time="25 min",
    restaurant_arrival_time=(datetime(2024, 10, 15, hour=6, tzinfo=LOS_ANGELES_TIMEZONE)),
    activity_start_time=(datetime(2024, 10, 15, hour=8, tzinfo=LOS_ANGELES_TIMEZONE)),
    restaurant=Restaurant(
        source_id=f"{uuid4()}",
        source=RestaurantSource.GOOGLE_PLACES,
        name="Zarape Cocina & Cantina",
        location=Location(
            directions_uri="https://g.co/kgs/o6Z9PpR",
            latitude=0,
            longitude=0,
            formatted_address="8351 Santa Monica Blvd, West Hollywood, CA, 90069",
        ),
        photos=Photos(
            cover_photo_uri="https://s3-media0.fl.yelpcdn.com/bphoto/NQFmn6sxr2RC-czWIBi8aw/o.jpg",
            supplemental_photo_uris=[
                "https://s3-media0.fl.yelpcdn.com/bphoto/MRvfdbtJJC6ur5Ifg1lFqA/o.jpg",
                "https://s3-media0.fl.yelpcdn.com/bphoto/ve0FaqvudsTj-GoQnbfwRw/o.jpg",
                "https://s3-media0.fl.yelpcdn.com/bphoto/DlYbaW4WEwsTjWEifG61Kg/o.jpg",
                "https://s3-media0.fl.yelpcdn.com/bphoto/ejPbmGcWhJsMSqkIJ6FwaA/o.jpg",
            ],
        ),
        reservable=True,
        rating=4.6,
        primary_type_name="Mexican Restaurant",
        website_uri="https://zarapecocinacantina.com/",
        description="Tacos, burritos and other traditional Mexican dishes served in a casual space with beer and margaritas.",
        parking_tips="Free open lot behind the building next to the market.",
        customer_favorites="Chicken Fajitas, Strawberry Margarita",
    ),
    activity=Activity(
        source_id=f"{uuid4()}",
        source=ActivitySource.EVENTBRITE,
        ticket_info=ActivityTicketInfo(
            type="General Admission",
            notes="Tickets will be delivered electronically to you via email. No assigned seating.",
            cost=2200,
            fee=150,
            tax=40,
        ),
        venue=ActivityVenue(
            name="The Comedy Store, Main Room",
            location=Location(
                directions_uri="https://g.co/kgs/h1SY9De",
                latitude=0,
                longitude=0,
                formatted_address="8433 Sunset Blvd, Hollywood, CA, 90069",
            ),
        ),
        photos=Photos(
            cover_photo_uri="https://image.rush49.com/rush49/images/comedystore-web1550864526.jpg",
            supplemental_photo_uris=[
                "https://image.arrivalguides.com/x/09/53c8f61769dc5bc3122df6c7f984f2c9.jpg",
                "https://ehqhynkh4tw.exactdn.com/wp-content/uploads/sites/2/2020/02/CSP-New-WO.jpg",
                "https://dynamic-media-cdn.tripadvisor.com/media/photo-o/01/ec/4e/a3/friday-night-on-sunset.jpg",
                "https://s3-media0.fl.yelpcdn.com/bphoto/EdO9HgeywKLmm2IGAv3eyA/348s.jpg",
            ],
        ),
        name="Headliners of the OR",
        description="This is where it all started. April 7th, 1972. This is the room where The Store became the home of American Comedy. Known for its intimate shows and late nights, The Original Room is the favorite space for super star comedians and after midnight heroes to test material, find their voices, and riff with the piano player.",
        website_uri="https://thecomedystore.com/",
        door_tips="Doors open at 7:30PM, Event begins at 8:00PM, Expected end time is 10:30PM",
        insider_tips="Order your two drink minimum all at once because it takes a while for the waitress to make the second round. If you sit in the front, expect to get picked on by the comedians.",
        parking_tips="Free open lot behind the building next to the market.",
    ),
)


@strawberry.input
class OutingInput:
    id: UUID


async def get_outing_query(*, info: strawberry.Info[GraphQLContext], input: OutingInput) -> Outing:
    return MOCK_OUTING # TODO: debug
    # return Outing(
    #     id=input.id,
    #     headcount=2,
    #     activity=None,
    #     restaurant=None,
    #     restaurant_arrival_time=None,
    #     activity_start_time=None,
    #     driving_time=None,
    # )
    async with database.async_session.begin() as db_session:
        outing_activity = await OutingActivityOrm.get_one_by_outing_id(
            session=db_session,
            outing_id=input.id,
        )
        outing_reservation = await OutingReservationOrm.get_one_by_outing_id(
            session=db_session,
            outing_id=input.id,
        )

    activity = await get_activity(
        source=outing_activity.source,
        source_id=outing_activity.source_id,
    )

    restaurant = await get_restaurant(
        source=outing_reservation.source,
        source_id=outing_reservation.source_id,
    )

    return Outing(
        id=input.id,
        headcount=max(outing_activity.headcount, outing_reservation.headcount),
        activity=activity,
        restaurant=restaurant,
        driving_time=None,
        activity_start_time=outing_activity.start_time_local,
        restaurant_arrival_time=outing_reservation.start_time_local,
    )
