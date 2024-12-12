import enum
from textwrap import dedent
from typing import Annotated
from uuid import UUID

import strawberry
import stripe

import eave.stdlib.slack
from eave.core import database
from eave.core.analytics import ANALYTICS
from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.resolvers.mutations.helpers.time_bounds_validator import (
    StartTimeTooLateError,
    StartTimeTooSoonError,
    validate_time_within_bounds_or_exception,
)
from eave.core.graphql.types.booking import (
    Booking,
)
from eave.core.lib.event_helpers import get_activity, get_restaurant
from eave.core.orm.account import AccountOrm
from eave.core.orm.base import InvalidRecordError
from eave.core.orm.booking import BookingActivityTemplateOrm, BookingOrm, BookingReservationTemplateOrm
from eave.core.orm.outing import OutingOrm
from eave.core.orm.reserver_details import ReserverDetailsOrm
from eave.core.shared.errors import ValidationError
from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.logging import LOGGER
from eave.stdlib.util import unwrap


@strawberry.input
class CreateBookingInput:
    outing_id: UUID
    reserver_details_id: UUID  # TODO: Should we get this from AccountOrm?


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
    account = unwrap(info.context.get("authenticated_account"))

    try:
        async with database.async_session.begin() as db_session:
            outing = await OutingOrm.get_one(db_session, input.outing_id)
            survey = outing.survey
            # stripe_payment_intent_reference_orm = (await db_session.scalars(StripePaymentIntentReferenceOrm.select(outing_id=outing.id))).one_or_none()

            # validate outing time still valid to book
            try:
                validate_time_within_bounds_or_exception(start_time=survey.start_time_utc, timezone=survey.timezone)
            except StartTimeTooSoonError:
                return CreateBookingFailure(failure_reason=CreateBookingFailureReason.START_TIME_TOO_SOON)
            except StartTimeTooLateError:
                return CreateBookingFailure(failure_reason=CreateBookingFailureReason.START_TIME_TOO_LATE)

            reserver_details = await ReserverDetailsOrm.get_one(
                db_session, account_id=account.id, uid=input.reserver_details_id
            )

            booking = BookingOrm(
                reserver_details=reserver_details,
                stripe_payment_intent_reference=stripe_payment_intent_reference_orm,
            )
            db_session.add(booking)

            booking.accounts = [account]

            for activity_orm in outing.activities:
                activity = await get_activity(source=activity_orm.source, source_id=activity_orm.source_id)

                if activity:
                    booking.activities.append(
                        BookingActivityTemplateOrm(
                            booking=booking,
                            source=activity_orm.source,
                            source_id=activity_orm.source_id,
                            name=activity.name,
                            start_time_utc=activity_orm.start_time_utc,
                            timezone=activity_orm.timezone,
                            headcount=activity_orm.headcount,
                            external_booking_link=activity.website_uri,
                            address=activity.venue.location.address,
                            coordinates=activity.venue.location.coordinates,
                            photo_uri=activity.photos.cover_photo.src if activity.photos.cover_photo else None,
                        )
                    )

            for reservation_orm in outing.reservations:
                reservation = await get_restaurant(
                    source=reservation_orm.source,
                    source_id=reservation_orm.source_id,
                )

                booking.reservations.append(
                    BookingReservationTemplateOrm(
                        booking=booking,
                        source=reservation_orm.source,
                        source_id=reservation_orm.source_id,
                        name=reservation.name,
                        start_time_utc=reservation_orm.start_time_utc,
                        timezone=reservation_orm.timezone,
                        headcount=reservation_orm.headcount,
                        external_booking_link=reservation.website_uri,
                        address=reservation.location.address,
                        coordinates=reservation.location.coordinates,
                        photo_uri=reservation.photos.cover_photo.src if reservation.photos.cover_photo else None,
                    )
                )

    except InvalidRecordError as e:
        LOGGER.exception(e)
        return CreateBookingFailure(
            failure_reason=CreateBookingFailureReason.VALIDATION_ERRORS, validation_errors=e.validation_errors
        )

    stripe_payment_intent = await stripe.PaymentIntent.get()

    await _notify_slack(booking=booking, account=account, reserver_details=reserver_details)

    ANALYTICS.track(
        event_name="booking created",
        account_id=account.id,
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


async def _notify_slack(
    booking: BookingOrm,
    account: AccountOrm,
    reserver_details: ReserverDetailsOrm,
) -> None:
    try:
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

                    Reserver first name: `{reserver_details.first_name}`
                    Reserver last name: `{reserver_details.last_name}`
                    Reserver phone number: `{reserver_details.phone_number}`

                    {"\n".join([
                    f"""*Reservation:*
                    for {reservation.headcount} attendees
                    on (ISO time): {reservation.start_time_local.isoformat()}
                    at
                    ```
                    {reservation.name}
                    {reservation.address}
                    ```
                    """
                        for reservation in booking.reservations
                    ])}

                    {"\n".join([
                    f"""*Activity:*
                    for {activity.headcount} attendees
                    on (ISO time): {activity.start_time_local.isoformat()}
                    at
                    ```
                    {activity.name}
                    {activity.address}
                    ```
                    """
                        for activity in booking.activities
                    ])}"""),
            )
    except Exception as e:
        LOGGER.exception(e)
