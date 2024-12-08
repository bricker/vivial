from uuid import UUID

import strawberry
from google.maps.places_v1 import PlacesAsyncClient

from eave.core import database
from eave.core.config import CORE_API_APP_CONFIG
from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.types.booking import BookingDetailPeek, BookingDetails
from eave.core.lib.event_helpers import get_activity, get_restuarant
from eave.core.orm.booking import BookingOrm
from eave.core.orm.booking_activities_template import BookingActivityTemplateOrm
from eave.core.orm.booking_reservations_template import BookingReservationTemplateOrm
from eave.core.shared.enums import ActivitySource, RestaurantSource
from eave.stdlib.eventbrite.client import EventbriteClient
from eave.stdlib.util import unwrap


async def _get_booking_details(
    booking_id: UUID,
) -> BookingDetails:
    places_client = PlacesAsyncClient()
    activities_client = EventbriteClient(api_key=CORE_API_APP_CONFIG.eventbrite_api_key)
    activities_query = BookingActivityTemplateOrm.select().where(BookingActivityTemplateOrm.booking_id == booking_id)
    reservations_query = BookingReservationTemplateOrm.select().where(
        BookingReservationTemplateOrm.booking_id == booking_id
    )

    async with database.async_session.begin() as session:
        # NOTE: only getting 1 (or None) result here instead of full scalars result since
        # response type only accepts one of each
        activity = await session.scalar(activities_query)
        reservation = await session.scalar(reservations_query)

    details = BookingDetails(
        id=booking_id,
        headcount=0,
        activity=None,
        activity_start_time=None,
        restaurant=None,
        restaurant_arrival_time=None,
        driving_time=None,  # TODO: can we fill this in?
    )

    if activity:
        details.activity_start_time = activity.start_time_local
        details.activity = await get_activity(
            event_id=activity.source_id,
            event_source=ActivitySource[activity.source],
            places_client=places_client,
            activities_client=activities_client,
        )
        details.headcount = max(details.headcount, activity.headcount)

    if reservation:
        details.restaurant_arrival_time = reservation.start_time_local
        details.restaurant = await get_restuarant(
            event_id=reservation.source_id,
            event_source=RestaurantSource[reservation.source],
            places_client=places_client,
        )
        details.headcount = max(details.headcount, reservation.headcount)

    return details


async def list_bookings_query(
    *,
    info: strawberry.Info[GraphQLContext],
) -> list[BookingDetailPeek]:
    account_id = unwrap(info.context.get("authenticated_account_id"))
    query = BookingOrm.select().where(BookingOrm.account_id == account_id)
    booking_details = []

    async with database.async_session.begin() as db_session:
        booking_orms = await db_session.scalars(query)

        for booking in booking_orms:
            activities_query = BookingActivityTemplateOrm.select().where(
                BookingActivityTemplateOrm.booking_id == booking.id
            )
            reservations_query = BookingReservationTemplateOrm.select().where(
                BookingReservationTemplateOrm.booking_id == booking.id
            )
            # NOTE: only getting 1 (or None) result here instead of full scalars result since
            # response type only accepts one of each
            activity = await db_session.scalar(activities_query)
            reservation = await db_session.scalar(reservations_query)
            photo_uri = None
            if reservation and reservation.photo_uri:
                photo_uri = reservation.photo_uri
            if activity and activity.photo_uri:
                photo_uri = activity.photo_uri

            booking_details.append(
                BookingDetailPeek(
                    id=booking.id,
                    activity_start_time=activity.start_time_local if activity else None,
                    activity_name=activity.name if activity else None,
                    restaurant_name=reservation.name if reservation else None,
                    restaurant_arrival_time=reservation.start_time_local if reservation else None,
                    photo_uri=photo_uri,
                )
            )

    return booking_details


@strawberry.input
class GetBookingDetailsQueryInput:
    booking_id: UUID


async def get_booking_details_query(
    *,
    info: strawberry.Info[GraphQLContext],
    input: GetBookingDetailsQueryInput,
) -> BookingDetails:
    account_id = unwrap(info.context.get("authenticated_account_id"))
    query = BookingOrm.select().where(BookingOrm.account_id == account_id).where(BookingOrm.id == input.booking_id)

    # validate the requesting account owns the booking requested
    async with database.async_session.begin() as db_session:
        booking_orm = (await db_session.scalars(query)).one()

    detail = await _get_booking_details(
        booking_id=booking_orm.id,
    )

    return detail
