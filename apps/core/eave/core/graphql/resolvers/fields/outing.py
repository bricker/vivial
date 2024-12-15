from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import strawberry

from eave.core import database
from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.types.activity import Activity, ActivityCategoryGroup, ActivityVenue
from eave.core.graphql.types.address import GraphQLAddress
from eave.core.graphql.types.location import Location
from eave.core.graphql.types.outing import (
    Outing,
)
from eave.core.graphql.types.photos import Photo, Photos
from eave.core.graphql.types.pricing import CostBreakdown
from eave.core.graphql.types.restaurant import Restaurant
from eave.core.graphql.types.search_region import SearchRegion
from eave.core.graphql.types.survey import Survey
from eave.core.graphql.types.ticket_info import TicketInfo
from eave.core.lib.event_helpers import get_activity, get_closest_search_region_to_point, get_restaurant
from eave.core.orm.activity_category_group import ActivityCategoryGroupOrm
from eave.core.orm.outing import OutingOrm
from eave.core.orm.search_region import SearchRegionOrm
from eave.core.shared.enums import ActivitySource, OutingBudget, RestaurantSource
from eave.core.shared.geo import GeoPoint
from eave.stdlib.time import LOS_ANGELES_TIMEZONE

# TODO: Remove once Date Picked UI is complete.
_mock_survey = Survey(
    id=uuid4(),
    budget=OutingBudget.INEXPENSIVE,
    headcount=2,
    search_regions=[SearchRegion.from_orm(orm) for orm in SearchRegionOrm.all()[0:2]],
    start_time=datetime.now(LOS_ANGELES_TIMEZONE) + timedelta(days=7),
)

_mock_activity = Activity(
    source_id=f"{uuid4()}",
    source=ActivitySource.EVENTBRITE,
    ticket_info=TicketInfo(
        name="General Admission",
        notes="Tickets will be delivered electronically to you via email. No assigned seating.",
        cost_breakdown=CostBreakdown(
            base_cost_cents=2200,
            fee_cents=150,
            tax_cents=40,
        ),
    ),
    venue=ActivityVenue(
        name="The Comedy Store, Main Room",
        location=Location(
            directions_uri="https://g.co/kgs/h1SY9De",
            coordinates=GeoPoint(
                lat=0,
                lon=0,
            ),
            address=GraphQLAddress(
                address1="8433 Sunset Blvd",
                address2=None,
                city="Hollywood",
                state="CA",
                country="US",
                zip_code="90069",
            ),
        ),
    ),
    photos=Photos(
        cover_photo=Photo(
            src="https://image.rush49.com/rush49/images/comedystore-web1550864526.jpg",
            alt="Alt Text",
            attributions=[],
            id=str(uuid4()),
        ),
        supplemental_photos=[
            Photo(
                src="https://image.arrivalguides.com/x/09/53c8f61769dc5bc3122df6c7f984f2c9.jpg",
                alt="Alt Text",
                attributions=[],
                id=str(uuid4()),
            ),
            Photo(
                src="https://ehqhynkh4tw.exactdn.com/wp-content/uploads/sites/2/2020/02/CSP-New-WO.jpg",
                alt="Alt Text",
                attributions=[],
                id=str(uuid4()),
            ),
            Photo(
                src="https://dynamic-media-cdn.tripadvisor.com/media/photo-o/01/ec/4e/a3/friday-night-on-sunset.jpg",
                alt="Alt Text",
                attributions=[],
                id=str(uuid4()),
            ),
            Photo(
                src="https://s3-media0.fl.yelpcdn.com/bphoto/EdO9HgeywKLmm2IGAv3eyA/348s.jpg",
                alt="Alt Text",
                attributions=[],
                id=str(uuid4()),
            ),
        ],
    ),
    name="Headliners of the OR",
    description="This is where it all started. April 7th, 1972. This is the room where The Store became the home of American Comedy. Known for its intimate shows and late nights, The Original Room is the favorite space for super star comedians and after midnight heroes to test material, find their voices, and riff with the piano player.",
    website_uri="https://thecomedystore.com/",
    door_tips="Doors open at 7:30PM, Event begins at 8:00PM, Expected end time is 10:30PM",
    insider_tips="Order your two drink minimum all at once because it takes a while for the waitress to make the second round. If you sit in the front, expect to get picked on by the comedians.",
    parking_tips="Free open lot behind the building next to the market.",
    category_group=ActivityCategoryGroup.from_orm(
        ActivityCategoryGroupOrm.one_or_exception(activity_category_group_id=UUID("988e0bf142564462985a2657602aad1b"))
    ),
)

MOCK_OUTING = Outing(
    id=uuid4(),
    survey=_mock_survey,
    driving_time="25 min",
    cost_breakdown=_mock_activity.ticket_info.cost_breakdown * _mock_survey.headcount
    if _mock_activity.ticket_info
    else CostBreakdown(),
    restaurant_arrival_time=_mock_survey.start_time,
    activity_start_time=_mock_survey.start_time + timedelta(hours=2),
    restaurant_region=SearchRegion.from_orm(SearchRegionOrm.all()[0]),
    activity_region=SearchRegion.from_orm(SearchRegionOrm.all()[1]),
    restaurant=Restaurant(
        source_id=f"{uuid4()}",
        source=RestaurantSource.GOOGLE_PLACES,
        name="Zarape Cocina & Cantina",
        location=Location(
            directions_uri="https://g.co/kgs/o6Z9PpR",
            address=GraphQLAddress(
                address1="8351 Santa Monica Blvd",
                address2=None,
                city="West Hollywood",
                state="CA",
                country="US",
                zip_code="90069",
            ),
            coordinates=GeoPoint(
                lat=0,
                lon=0,
            ),
        ),
        photos=Photos(
            cover_photo=Photo(
                id=str(uuid4()),
                src="https://s3-media0.fl.yelpcdn.com/bphoto/NQFmn6sxr2RC-czWIBi8aw/o.jpg",
                alt="Alt Text",
                attributions=[],
            ),
            supplemental_photos=[
                Photo(
                    id=str(uuid4()),
                    src="https://s3-media0.fl.yelpcdn.com/bphoto/MRvfdbtJJC6ur5Ifg1lFqA/o.jpg",
                    alt="Alt Text",
                    attributions=[],
                ),
                Photo(
                    id=str(uuid4()),
                    src="https://s3-media0.fl.yelpcdn.com/bphoto/ve0FaqvudsTj-GoQnbfwRw/o.jpg",
                    alt="Alt Text",
                    attributions=[],
                ),
                Photo(
                    id=str(uuid4()),
                    src="https://s3-media0.fl.yelpcdn.com/bphoto/DlYbaW4WEwsTjWEifG61Kg/o.jpg",
                    alt="Alt Text",
                    attributions=[],
                ),
                Photo(
                    id=str(uuid4()),
                    src="https://s3-media0.fl.yelpcdn.com/bphoto/ejPbmGcWhJsMSqkIJ6FwaA/o.jpg",
                    alt="Alt Text",
                    attributions=[],
                ),
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
    activity=_mock_activity,
)


@strawberry.input
class OutingInput:
    id: UUID


async def get_outing_query(*, info: strawberry.Info[GraphQLContext], input: OutingInput) -> Outing | None:
    async with database.async_session.begin() as db_session:
        outing = await OutingOrm.get_one(db_session, input.id)

    activity: Activity | None = None
    restaurant: Restaurant | None = None
    headcount = 0
    activity_start_time: datetime | None = None
    restaurant_arrival_time: datetime | None = None
    activity_region: SearchRegionOrm | None = None
    restaurant_region: SearchRegionOrm | None = None
    cost_breakdown = CostBreakdown()

    regions = [SearchRegionOrm.one_or_exception(search_region_id=area_id) for area_id in outing.survey.search_area_ids]

    if len(outing.activities) > 0:
        # Currently the client only supports 1 activity per outing.
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

        if activity:
            if activity.ticket_info:
                cost_breakdown = activity.ticket_info.cost_breakdown * outing.survey.headcount

            activity_region = get_closest_search_region_to_point(
                regions=regions, point=activity.venue.location.coordinates
            )

    if len(outing.reservations) > 0:
        # Currently the client only supports 1 restaurant per outing.
        outing_reservation = outing.reservations[0]
        headcount = max(headcount, outing_reservation.headcount)
        restaurant_arrival_time = outing_reservation.start_time_local

        restaurant = await get_restaurant(
            source=outing_reservation.source,
            source_id=outing_reservation.source_id,
        )

        if restaurant:
            restaurant_region = get_closest_search_region_to_point(
                regions=regions, point=restaurant.location.coordinates
            )

    return Outing(
        id=outing.id,
        survey=Survey.from_orm(outing.survey),
        cost_breakdown=cost_breakdown,
        activity=activity,
        restaurant=restaurant,
        driving_time=None,
        activity_start_time=activity_start_time,
        restaurant_arrival_time=restaurant_arrival_time,
        activity_region=SearchRegion.from_orm(activity_region) if activity_region else None,
        restaurant_region=SearchRegion.from_orm(restaurant_region) if restaurant_region else None,
    )
