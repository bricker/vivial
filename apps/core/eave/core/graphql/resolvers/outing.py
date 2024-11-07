from datetime import datetime
from uuid import UUID, uuid4

import strawberry

from eave.core.graphql.types.activity import Activity, ActivityTicketInfo, ActivityVenue
from eave.core.graphql.types.location import Location
from eave.core.graphql.types.outing import (
    Outing,
    PlanOutingResult,
    ReplanOutingError,
    ReplanOutingErrorCode,
    ReplanOutingInput,
    OutingBudget,
    PlanOutingSuccess,
    ReplanOutingResult,
    ReplanOutingSuccess,
)
from eave.core.graphql.types.photos import Photos
from eave.core.graphql.types.restaurant import Restaurant
from eave.core.internal import database
from eave.core.internal.orm.outing import OutingOrm
from eave.core.internal.orm.outing_activity import OutingActivityOrm
from eave.core.internal.orm.outing_reservation import OutingReservationOrm
from eave.core.outing.constants.zoneinfo import LOS_ANGELES_ZONE_INFO
from eave.core.outing.models.search_region_code import SearchRegionCode
from eave.core.outing.models.sources import ActivitySource, RestaurantSource
from eave.stdlib.core_api.models.enums import ReservationSource

from ..types.user import UserInput

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
        source=RestaurantSource.GOOGLE_PLACES,
        name="Zarape Cocina & Cantina",
        location=Location(
            internal_area_id=SearchRegionCode.US_CA_LA1,
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
                internal_area_id=SearchRegionCode.US_CA_LA2,
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


async def create_outing_plan(
    visitor_id: UUID,
    survey_id: UUID,
    account_id: UUID | None,
) -> OutingOrm:
    # TODO: actually call the planning function instead
    async with database.async_session.begin() as db_session:
        outing = await OutingOrm.create(
            session=db_session,
            visitor_id=visitor_id,
            survey_id=survey_id,
            account_id=account_id,
        )
        _outing_activity = await OutingActivityOrm.create(
            session=db_session,
            outing_id=outing.id,
            activity_id=str(uuid4()),
            activity_source=ActivitySource.EVENTBRITE,
            activity_start_time=datetime.now(),
            num_attendees=2,
        )
        _outing_reservation = await OutingReservationOrm.create(
            session=db_session,
            outing_id=outing.id,
            reservation_id=str(uuid4()),
            reservation_source=ReservationSource.GOOGLE_PLACES,
            reservation_start_time=datetime.now(),
            num_attendees=2,
        )
    return outing


async def plan_outing_mutation(
    *,
    info: strawberry.Info,
    visitor_id: UUID,
    group: list[UserInput],
    start_time: datetime,
    search_area_ids: list[str],
    budget: OutingBudget,
    headcount: int,
) -> PlanOutingResult:
    # try:
    #     async with database.async_session.begin() as db_session:
    #         search_areas: list[SearchRegionCode] = []
    #         for area_id in search_area_ids:
    #             if region := SearchRegionCode.from_str(area_id):
    #                 search_areas.append(region)
    #         survey = await SurveyOrm.create(
    #             session=db_session,
    #             visitor_id=visitor_id,
    #             start_time=start_time,
    #             search_area_ids=search_areas,
    #             budget=budget,
    #             headcount=headcount,
    #             account_id=None,  # TODO: look for auth attached to request
    #         )
    # except InvalidDataError as e:
    #     LOGGER.exception(e)
    #     return SubmitSurveyError(error_code=SubmitSurveyErrorCode(e.code))

    # outing = await create_outing_plan(
    #     visitor_id=survey.visitor_id,
    #     survey_id=survey.id,
    #     account_id=survey.account_id,
    # )

    return PlanOutingSuccess(outing=MOCK_OUTING)


async def replan_outing_mutation(
    *,
    info: strawberry.Info,
    input: ReplanOutingInput,
) -> ReplanOutingResult:
    # try:
    #     async with database.async_session.begin() as db_session:
    #         original_outing = await OutingOrm.one_or_exception(
    #             session=db_session,
    #             params=OutingOrm.QueryParams(id=outing_id),
    #         )
    #         survey = await SurveyOrm.one_or_exception(
    #             session=db_session, params=SurveyOrm.QueryParams(id=original_outing.survey_id)
    #         )

    #         validate_time_within_bounds_or_exception(survey.start_time)

    #     outing = await create_outing_plan(
    #         visitor_id=visitor_id,
    #         survey_id=original_outing.survey_id,
    #         account_id=original_outing.account_id,  # TODO: this is wrong; look for any auth attached to the request instead
    #     )
    # except InvalidDataError as e:
    #     LOGGER.exception(e)
    #     return ReplanOutingError(error_code=ReplanOutingErrorCode(e.code))
    # except StartTimeTooLateError as e:
    #     LOGGER.exception(e)
    #     return ReplanOutingError(error_code=ReplanOutingErrorCode.START_TIME_TOO_LATE)
    # except StartTimeTooSoonError as e:
    #     LOGGER.exception(e)
    #     return ReplanOutingError(error_code=ReplanOutingErrorCode.START_TIME_TOO_SOON)

    return ReplanOutingSuccess(outing=MOCK_OUTING)
