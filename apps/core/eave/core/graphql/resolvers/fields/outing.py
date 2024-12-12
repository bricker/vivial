from datetime import UTC, datetime, timedelta
from uuid import UUID

import strawberry

from eave.core import database
from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.types.outing import (
    Outing,
)
from eave.core.graphql.types.survey import Survey
from eave.core.lib.event_helpers import get_activity, get_restaurant
from eave.core.orm.outing import OutingOrm

# # TODO: Remove once we're fetching from the appropriate sources.
# MOCK_OUTING = Outing(
#     id=uuid4(),
#     headcount=2,
#     driving_time="25 min",
#     restaurant_arrival_time=(datetime(2024, 10, 15, hour=6, tzinfo=LOS_ANGELES_TIMEZONE)),
#     activity_start_time=(datetime(2024, 10, 15, hour=8, tzinfo=LOS_ANGELES_TIMEZONE)),
#     restaurant=Restaurant(
#         source_id=f"{uuid4()}",
#         source=RestaurantSource.GOOGLE_PLACES,
#         name="Zarape Cocina & Cantina",
#         location=Location(
#             directions_uri="https://g.co/kgs/o6Z9PpR",
#             latitude=0,
#             longitude=0,
#             formatted_address="8351 Santa Monica Blvd, West Hollywood, CA, 90069",
#         ),
#         photos=Photos(
#             cover_photo_uri="https://s3-media0.fl.yelpcdn.com/bphoto/NQFmn6sxr2RC-czWIBi8aw/o.jpg",
#             supplemental_photo_uris=[
#                 "https://s3-media0.fl.yelpcdn.com/bphoto/MRvfdbtJJC6ur5Ifg1lFqA/o.jpg",
#                 "https://s3-media0.fl.yelpcdn.com/bphoto/ve0FaqvudsTj-GoQnbfwRw/o.jpg",
#                 "https://s3-media0.fl.yelpcdn.com/bphoto/DlYbaW4WEwsTjWEifG61Kg/o.jpg",
#                 "https://s3-media0.fl.yelpcdn.com/bphoto/ejPbmGcWhJsMSqkIJ6FwaA/o.jpg",
#             ],
#         ),
#         reservable=True,
#         rating=4.6,
#         primary_type_name="Mexican Restaurant",
#         website_uri="https://zarapecocinacantina.com/",
#         description="Tacos, burritos and other traditional Mexican dishes served in a casual space with beer and margaritas.",
#         parking_tips="Free open lot behind the building next to the market.",
#         customer_favorites="Chicken Fajitas, Strawberry Margarita",
#     ),
#     activity=Activity(
#         source_id=f"{uuid4()}",
#         source=ActivitySource.EVENTBRITE,
#         ticket_info=ActivityTicketInfo(
#             type="General Admission",
#             notes="Tickets will be delivered electronically to you via email. No assigned seating.",
#             cost_cents=2200,
#             fee_cents=150,
#             tax_cents=40,
#         ),
#         venue=ActivityVenue(
#             name="The Comedy Store, Main Room",
#             location=Location(
#                 directions_uri="https://g.co/kgs/h1SY9De",
#                 latitude=0,
#                 longitude=0,
#                 formatted_address="8433 Sunset Blvd, Hollywood, CA, 90069",
#             ),
#         ),
#         photos=Photos(
#             cover_photo_uri="https://image.rush49.com/rush49/images/comedystore-web1550864526.jpg",
#             supplemental_photo_uris=[
#                 "https://image.arrivalguides.com/x/09/53c8f61769dc5bc3122df6c7f984f2c9.jpg",
#                 "https://ehqhynkh4tw.exactdn.com/wp-content/uploads/sites/2/2020/02/CSP-New-WO.jpg",
#                 "https://dynamic-media-cdn.tripadvisor.com/media/photo-o/01/ec/4e/a3/friday-night-on-sunset.jpg",
#                 "https://s3-media0.fl.yelpcdn.com/bphoto/EdO9HgeywKLmm2IGAv3eyA/348s.jpg",
#             ],
#         ),
#         name="Headliners of the OR",
#         description="This is where it all started. April 7th, 1972. This is the room where The Store became the home of American Comedy. Known for its intimate shows and late nights, The Original Room is the favorite space for super star comedians and after midnight heroes to test material, find their voices, and riff with the piano player.",
#         website_uri="https://thecomedystore.com/",
#         door_tips="Doors open at 7:30PM, Event begins at 8:00PM, Expected end time is 10:30PM",
#         insider_tips="Order your two drink minimum all at once because it takes a while for the waitress to make the second round. If you sit in the front, expect to get picked on by the comedians.",
#         parking_tips="Free open lot behind the building next to the market.",
#     ),
# )


async def get_outing_query(*, info: strawberry.Info[GraphQLContext], outing_id: UUID) -> Outing | None:
    async with database.async_session.begin() as db_session:
        outing = await OutingOrm.get_one(db_session, outing_id)

        activity = None
        restaurant = None
        headcount = 0
        activity_start_time = None
        restaurant_arrival_time = None

        if len(outing.activities) > 0:
            outing_activity = outing.activities[0]
            # This is a quick way to expire an outing URL 24 hours before the outing beings.
            if outing_activity.start_time_utc < (datetime.now(UTC) + timedelta(hours=24)):
                return None

            headcount = max(headcount, outing_activity.headcount)
            activity_start_time = outing_activity.start_time_local

            activity = await get_activity(
                source=outing_activity.source,
                source_id=outing_activity.source_id,
            )

        if len(outing.reservations) > 0:
            outing_reservation = outing.reservations[0]
            headcount = max(headcount, outing_reservation.headcount)
            restaurant_arrival_time = outing_reservation.start_time_local

            restaurant = await get_restaurant(
                source=outing_reservation.source,
                source_id=outing_reservation.source_id,
            )

    return Outing(
        id=outing_id,
        headcount=headcount,
        activity=activity,
        restaurant=restaurant,
        driving_time=None,
        activity_start_time=activity_start_time,
        restaurant_arrival_time=restaurant_arrival_time,
        survey=Survey.from_orm(outing.survey),
    )
