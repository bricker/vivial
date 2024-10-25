from uuid import UUID

import strawberry
from sqlalchemy.ext.asyncio import AsyncSession

from eave.core.graphql.types.booking import (
    Booking,
    CreateBookingError,
    CreateBookingErrorCode,
    CreateBookingResult,
    CreateBookingSuccess,
)
from eave.core.internal import database
from eave.core.internal.orm.account_booking import AccountBookingOrm
from eave.core.internal.orm.booking import BookingOrm
from eave.core.internal.orm.booking_activities_template import BookingActivityTemplateOrm
from eave.core.internal.orm.booking_reservations_template import BookingReservationTemplateOrm
from eave.core.internal.orm.outing import OutingOrm
from eave.core.internal.orm.outing_activity import OutingActivityOrm
from eave.core.internal.orm.outing_reservation import OutingReservationOrm
from eave.core.internal.orm.survey import SurveyOrm
from eave.core.internal.orm.util import validate_time_within_bounds_or_exception
from eave.stdlib.exceptions import InvalidDataError, StartTimeTooLateError, StartTimeTooSoonError
from eave.stdlib.logging import LOGGER


async def _create_templates_from_outing(
    db_session: AsyncSession,
    booking_id: UUID,
    outing: OutingOrm,
) -> None:
    activities = await OutingActivityOrm.query(
        session=db_session,
        params=OutingActivityOrm.QueryParams(outing_id=outing.id),
    )
    for activity in activities:
        # TODO: fetch activity details from remote src

        await BookingActivityTemplateOrm.create(
            session=db_session,
            booking_id=booking_id,
            activity_name="Biking in McDonalds parking lot",
            activity_start_time=activity.activity_start_time,
            num_attendees=activity.num_attendees,
            booking_link="https://micndontlds.com",
            activity_location_address1="101 Mcdonald St",
            activity_location_address2="Unit 666",
            activity_location_city="LA",
            activity_location_region="CA",
            activity_location_country="USA",
            activity_location_latitude=0,
            activity_location_longitude=0,
        )

    reservations = await OutingReservationOrm.query(
        session=db_session,
        params=OutingReservationOrm.QueryParams(outing_id=outing.id),
    )
    for reservation in reservations:
        # TODO: fetch dteails from remote

        await BookingReservationTemplateOrm.create(
            session=db_session,
            booking_id=booking_id,
            reservation_name="Red lobster dumpster",
            reservation_start_time=reservation.reservation_start_time,
            num_attendees=reservation.num_attendees,
            booking_link="https://redlobster.yum",
            reservation_location_address1="3269 Abandoned Alley Way",
            reservation_location_address2="",
            reservation_location_city="LA",
            reservation_location_region="CA",
            reservation_location_country="USA",
            reservation_location_latitude=0,
            reservation_location_longitude=1,
        )


async def create_booking_mutation(
    *,
    info: strawberry.Info,
    account_id: UUID,  # TODO: need this here? or get auth from elsewhere?
    outing_id: UUID,
    reserver_details_id: UUID,
) -> CreateBookingResult:
    try:
        async with database.async_session.begin() as db_session:
            # TODO: should we 1 or none and return client friendly error if 404? instead of 500 throw
            outing = await OutingOrm.one_or_exception(
                session=db_session,
                params=OutingOrm.QueryParams(id=outing_id),
            )
            survey = await SurveyOrm.one_or_exception(
                session=db_session, params=SurveyOrm.QueryParams(id=outing.survey_id)
            )
            # validate outing time still valid to book
            try:
                validate_time_within_bounds_or_exception(survey.start_time)
            except StartTimeTooSoonError:
                raise InvalidDataError(code=CreateBookingErrorCode.START_TIME_TOO_SOON)
            except StartTimeTooLateError:
                raise InvalidDataError(code=CreateBookingErrorCode.START_TIME_TOO_LATE)

            booking = await BookingOrm.create(
                session=db_session,
                reserver_details_id=reserver_details_id,
            )

            await AccountBookingOrm.create(
                session=db_session,
                account_id=account_id,
                booking_id=booking.id,
            )
            await _create_templates_from_outing(
                db_session=db_session,
                booking_id=booking.id,
                outing=outing,
            )
    except InvalidDataError as e:
        LOGGER.exception(e)
        return CreateBookingError(error_code=CreateBookingErrorCode(e.code))

    return CreateBookingSuccess(
        booking=Booking(
            id=booking.id,
            reserver_details_id=booking.reserver_details_id,
        )
    )
