import enum
from textwrap import dedent
from typing import Annotated
from uuid import UUID

import strawberry
from attr import dataclass
from sqlalchemy.ext.asyncio import AsyncSession

import eave.stdlib.slack
from eave.core import database
from eave.core.analytics import ANALYTICS
from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.types.booking import (
    Booking,
)
from eave.core.orm.account import AccountOrm
from eave.core.orm.account_booking import AccountBookingOrm
from eave.core.orm.address_types import PostgisStdaddr
from eave.core.orm.base import InvalidRecordError
from eave.core.orm.booking import BookingOrm
from eave.core.orm.booking_activities_template import BookingActivityTemplateOrm
from eave.core.orm.booking_reservations_template import BookingReservationTemplateOrm
from eave.core.orm.outing import OutingOrm
from eave.core.orm.outing_activity import OutingActivityOrm
from eave.core.orm.outing_reservation import OutingReservationOrm
from eave.core.orm.reserver_details import ReserverDetailsOrm
from eave.core.orm.survey import SurveyOrm
from eave.core.orm.util import StartTimeTooLateError, StartTimeTooSoonError, validate_time_within_bounds_or_exception
from eave.core.shared.errors import ValidationError
from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.logging import LOGGER
from eave.stdlib.util import unwrap


@dataclass
class BookingDetails:
    activities: list[BookingActivityTemplateOrm]
    reservations: list[BookingReservationTemplateOrm]


async def _create_templates_from_outing(
    db_session: AsyncSession,
    booking_id: UUID,
    outing: OutingOrm,
) -> BookingDetails:
    activities = await db_session.scalars(OutingActivityOrm.select().where(OutingActivityOrm.outing_id == outing.id))
    activity_details = []
    for activity in activities:
        # TODO: fetch activity details from remote src

        activity_details.append(
            await BookingActivityTemplateOrm.build(
                booking_id=booking_id,
                activity_name="Biking in McDonalds parking lot",
                activity_start_time=activity.activity_start_time,
                num_attendees=activity.num_attendees,
                external_booking_link="https://micndontlds.com",
                address=PostgisStdaddr(
                    house_num="101",
                    name="Mcdonald",
                    suftype="St",
                    unit="666",
                    city="LA",
                    state="CA",
                    country="USA",
                ),
                lat=0,
                lon=0,
            ).save(db_session)
        )

    reservations = await db_session.scalars(
        OutingReservationOrm.select().where(OutingReservationOrm.outing_id == outing.id)
    )
    reservation_details = []
    for reservation in reservations:
        # TODO: fetch dteails from remote

        reservation_details.append(
            await BookingReservationTemplateOrm.build(
                booking_id=booking_id,
                reservation_name="Red lobster dumpster",
                reservation_start_time=reservation.reservation_start_time,
                num_attendees=reservation.num_attendees,
                external_booking_link="https://redlobster.yum",
                address=PostgisStdaddr(
                    house_num="3269",
                    name="Abandoned Alley",
                    suftype="Way",
                    city="LA",
                    state="CA",
                    country="USA",
                ),
                lat=0,
                lon=1,
            ).save(db_session)
        )

    return BookingDetails(
        activities=activity_details,
        reservations=reservation_details,
    )


async def _notify_slack(
    booking_details: BookingDetails,
    account_id: UUID,
    reserver_details_id: UUID,
) -> None:
    async with database.async_session.begin() as db_session:
        account = await db_session.get_one(AccountOrm, account_id)
        reserver = await db_session.get_one(ReserverDetailsOrm, reserver_details_id)

    try:
        # TODO: This should happen in a pubsub subscriber on the "eave_account_registration" event.
        # Notify #sign-ups Slack channel.

        channel_id = SHARED_CONFIG.eave_slack_signups_channel_id
        slack_client = eave.stdlib.slack.get_authenticated_eave_system_slack_client()

        if slack_client and channel_id:
            slack_response = await slack_client.chat_postMessage(
                channel=channel_id,
                text="Someone just booked an outing!",
            )

            # TODO: distinguish whether any action on our part is needed for one or both options?
            await slack_client.chat_postMessage(
                channel=channel_id,
                thread_ts=slack_response.get("ts"),
                text=dedent(f"""
                    Account ID: `{account.id}`
                    Account email: `{account.email}`

                    Reserver first name: `{reserver.first_name}`
                    Reserver last name: `{reserver.last_name}`
                    Reserver phone number: `{reserver.phone_number}`

                    {"\n".join([
                    f"""*Reservation:*
                    for {reservation.num_attendees} attendees
                    on (ISO time): {reservation.reservation_start_time.isoformat()}
                    at
                    ```
                    {reservation.reservation_name}
                    {reservation.address}
                    ```
                    """
                        for reservation in booking_details.reservations
                    ])}

                    {"\n".join([
                    f"""*Activity:*
                    for {activity.num_attendees} attendees
                    on (ISO time): {activity.activity_start_time.isoformat()}
                    at
                    ```
                    {activity.activity_name}
                    {activity.address}
                    ```
                    """
                        for activity in booking_details.activities
                    ])}
                    """),
            )
    except Exception as e:
        LOGGER.exception(e)


@strawberry.input
class CreateBookingInput:
    outing_id: UUID
    reserver_details_id: UUID


@strawberry.type
class CreateBookingSuccess:
    booking: Booking


@strawberry.enum
class CreateBookingFailureReason(enum.Enum):
    START_TIME_TOO_SOON = enum.auto()
    START_TIME_TOO_LATE = enum.auto()
    VALIDATION_ERRORS = enum.auto()


@strawberry.type
class CreateBookingFailure:
    failure_reason: CreateBookingFailureReason
    validation_errors: list[ValidationError] | None = None


CreateBookingResult = Annotated[CreateBookingSuccess | CreateBookingFailure, strawberry.union("CreateBookingResult")]


async def create_booking_mutation(
    *,
    info: strawberry.Info[GraphQLContext],
    input: CreateBookingInput,
) -> CreateBookingResult:
    account_id = unwrap(info.context.get("authenticated_account_id"))

    try:
        async with database.async_session.begin() as db_session:
            # TODO: should we 1 or none and return client friendly error if 404? instead of 500 throw
            outing = await OutingOrm.get_one(db_session, input.outing_id)
            survey = await SurveyOrm.get_one(db_session, outing.survey_id)

            # validate outing time still valid to book
            try:
                validate_time_within_bounds_or_exception(survey.start_time)
            except StartTimeTooSoonError:
                return CreateBookingFailure(failure_reason=CreateBookingFailureReason.START_TIME_TOO_SOON)
            except StartTimeTooLateError:
                return CreateBookingFailure(failure_reason=CreateBookingFailureReason.START_TIME_TOO_LATE)

            booking = await BookingOrm.build(
                reserver_details_id=input.reserver_details_id,
            ).save(db_session)

            await AccountBookingOrm.build(
                account_id=account_id,
                booking_id=booking.id,
            ).save(db_session)

            booking_details = await _create_templates_from_outing(
                db_session=db_session,
                booking_id=booking.id,
                outing=outing,
            )
    except InvalidRecordError as e:
        LOGGER.exception(e)
        return CreateBookingFailure(
            failure_reason=CreateBookingFailureReason.VALIDATION_ERRORS, validation_errors=e.validation_errors
        )

    await _notify_slack(booking_details, account_id, input.reserver_details_id)

    ANALYTICS.track(
        event_name="booking created",
        account_id=account_id,
        extra_properties={
            "booking_constraints": {
                "headcount": survey.headcount,
                "budget": survey.budget,
                "search_areas": survey.search_area_ids,
            }
        },
    )

    return CreateBookingSuccess(
        booking=Booking.from_orm(booking),
    )
