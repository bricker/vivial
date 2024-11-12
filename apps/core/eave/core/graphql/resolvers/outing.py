from datetime import datetime
from uuid import UUID, uuid4

import strawberry

from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.types.activity import Activity, EventSource, ActivityTicketInfo, ActivityVenue
from eave.core.graphql.types.location import Location
from eave.core.graphql.types.outing import (
    Outing,
    OutingBudget,
)
from eave.core.graphql.types.photos import Photos
from eave.core.graphql.types.restaurant import Restaurant, EventSource
from eave.core.zoneinfo import LOS_ANGELES_ZONE_INFO

# TODO: Remove once we're fetching from the appropriate sources.
MOCK_OUTING = Outing(
    id=uuid4(),
    visitor_id=uuid4(),
    account_id=uuid4(),
    survey_id=uuid4(),
    budget=OutingBudget.THREE,
    headcount=2,
    driving_time="25 min",
    restaurant_arrival_time=(datetime(2024, 10, 15, hour=6, tzinfo=LOS_ANGELES_ZONE_INFO)),
    activity_start_time=(datetime(2024, 10, 15, hour=8, tzinfo=LOS_ANGELES_ZONE_INFO)),
    restaurant=Restaurant(
        source=EventSource.GOOGLE_PLACES,
        name="Zarape Cocina & Cantina",
        location=Location(
            search_region_id=UUID("354c2020-6227-46c1-be04-6f5965ba452d"),
            directions_uri="https://g.co/kgs/o6Z9PpR",
            address_1="8351 Santa Monica Blvd",
            address_2=None,
            city="West Hollywood",
            state="CA",
            zip_code="90069",
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
        source=EventSource.EVENTBRITE,
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
                search_region_id=UUID("354c2020-6227-46c1-be04-6f5965ba452d"),
                directions_uri="https://g.co/kgs/h1SY9De",
                address_1="8433 Sunset Blvd",
                address_2=None,
                city="Hollywood",
                state="CA",
                zip_code="90069",
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


async def get_outing_query(*, info: strawberry.Info[GraphQLContext], outing_id: UUID) -> Outing:
    # TODO: Fetch outing by outing_id.
    return MOCK_OUTING
