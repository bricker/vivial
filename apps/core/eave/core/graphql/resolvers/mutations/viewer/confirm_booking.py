import enum
from datetime import datetime
from textwrap import dedent
from typing import Annotated
from uuid import UUID

import strawberry
import stripe

import eave.stdlib.slack
from eave.core import database
from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.resolvers.mutations.helpers.create_outing import get_total_cost_cents
from eave.core.graphql.types.booking import (
    Booking,
)
from eave.core.graphql.types.survey import Survey
from eave.core.graphql.validators.time_bounds_validator import (
    start_time_too_soon,
)
from eave.core.lib.analytics_client import ANALYTICS
from eave.core.lib.google_places import GooglePlacesUtility
from eave.core.mail import BookingConfirmationData, EventItem, send_booking_confirmation_email
from eave.core.orm.account import AccountOrm
from eave.core.orm.booking import BookingOrm
from eave.core.shared.enums import ActivitySource, BookingState
from eave.core.shared.errors import ValidationError
from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.logging import LOGGER
from eave.stdlib.util import num_with_english_suffix, unwrap


@strawberry.input
class ConfirmBookingInput:
    booking_id: UUID


@strawberry.type
class ConfirmBookingSuccess:
    booking: Booking


@strawberry.enum
class ConfirmBookingFailureReason(enum.Enum):
    PAYMENT_REQUIRED = enum.auto()
    BOOKING_NOT_FOUND = enum.auto()
    START_TIME_TOO_SOON = enum.auto()
    START_TIME_TOO_LATE = enum.auto()


@strawberry.type
class ConfirmBookingFailure:
    failure_reason: ConfirmBookingFailureReason
    validation_errors: list[ValidationError] | None = None


ConfirmBookingResult = Annotated[
    ConfirmBookingSuccess | ConfirmBookingFailure, strawberry.union("ConfirmBookingResult")
]


async def confirm_booking_mutation(
    *,
    info: strawberry.Info[GraphQLContext],
    input: ConfirmBookingInput,
) -> ConfirmBookingResult:
    account_id = unwrap(info.context.get("authenticated_account_id"))
    visitor_id = info.context.get("visitor_id")

    async with database.async_session.begin() as db_session:
        account_orm = await AccountOrm.get_one(db_session, account_id)
        # It's important that when getting the booking, we use BOTH the account ID and booking ID.
        # Otherwise, it would be possible to confirm any booking, even ones you don't own.
        booking_orm = account_orm.get_booking(booking_id=input.booking_id)

    if not booking_orm:
        return ConfirmBookingFailure(failure_reason=ConfirmBookingFailureReason.BOOKING_NOT_FOUND)

    if booking_orm.state != BookingState.INITIATED:
        # If this booking was already confirmed, then just return the success state,
        # so we don't try to charge their card again and stuff.
        return ConfirmBookingSuccess(
            booking=Booking.from_orm(booking_orm),
        )

    if start_time_too_soon(start_time=booking_orm.start_time_utc, timezone=booking_orm.timezone):
        return ConfirmBookingFailure(failure_reason=ConfirmBookingFailureReason.START_TIME_TOO_SOON)

    if booking_orm.stripe_payment_intent_reference:
        # Get the given payment intent from the Stripe API
        stripe_payment_intent = await stripe.PaymentIntent.retrieve_async(
            id=booking_orm.stripe_payment_intent_reference.stripe_payment_intent_id,
        )

        # Validate that the payment intent has been authorized, but the funds haven't been captured.
        # This is important because if the payment authorization failed, we shouldn't create the booking.
        if stripe_payment_intent.status not in ["success", "requires_capture"]:
            LOGGER.error("invalid stripe payment intent status")
            return ConfirmBookingFailure(failure_reason=ConfirmBookingFailureReason.PAYMENT_REQUIRED)
    else:
        stripe_payment_intent = None

    # Although we already checked the cost in the `initiate booking` operation,
    # It's important that we double-check it here too, in case the real cost changed.
    # It's not enough to store the pre-calculated cost in the database somewhere, because that can become out of date.
    booking_total_cost_cents = await get_total_cost_cents(booking_orm)

    if booking_total_cost_cents > 0:
        # If the outing costs any money, then:

        # Validate that there is a payment intent.
        if not stripe_payment_intent:
            LOGGER.error("No payment intent available for paid outing")
            return ConfirmBookingFailure(failure_reason=ConfirmBookingFailureReason.PAYMENT_REQUIRED)

        # Validate that the authorized amount for the payment intent can cover the cost of the outing.
        if stripe_payment_intent.amount < booking_total_cost_cents:
            # We authorized an amount less than the actual cost of the outing.
            # If the authorization ended up being _more_, then we'll only capture the necessary amount when the funds are captured.
            LOGGER.error("Authorization amount too low for outing")
            return ConfirmBookingFailure(failure_reason=ConfirmBookingFailureReason.PAYMENT_REQUIRED)

    async with database.async_session.begin() as db_session:
        db_session.add(booking_orm)

        if booking_orm.reserver_details is None:
            if default_reserver_details := account_orm.get_default_reserver_details():
                # Hacky way to make sure some reserver details are set.
                # There is still a possibility that they won't be, though.
                booking_orm.reserver_details = default_reserver_details

        booking_orm.state = BookingState.CONFIRMED

    await perform_post_confirm_actions(
        booking_orm=booking_orm,
        account_orm=account_orm,
        visitor_id=visitor_id,
        total_cost_cents=booking_total_cost_cents,
    )

    return ConfirmBookingSuccess(
        booking=Booking.from_orm(booking_orm),
    )


async def perform_post_confirm_actions(
    *, booking_orm: BookingOrm, account_orm: AccountOrm, visitor_id: str | None, total_cost_cents: int
) -> None:
    # TODO: Move all of this into an offline queue
    _fire_booking_confirmation_email(account_orm=account_orm, booking_orm=booking_orm)
    _fire_analytics_booking_confirmed(
        booking_orm=booking_orm, account_orm=account_orm, visitor_id=visitor_id, total_cost_cents=total_cost_cents
    )
    await _notify_slack_booking_confirmed(
        booking_orm=booking_orm, account_orm=account_orm, total_cost_cents=total_cost_cents
    )


def _fire_analytics_booking_confirmed(
    *, booking_orm: BookingOrm, account_orm: AccountOrm, visitor_id: str | None, total_cost_cents: int
) -> None:
    ANALYTICS.track(
        event_name="booking_complete",
        account_id=account_orm.id,
        visitor_id=visitor_id,
        extra_properties={
            "booking_id": str(booking_orm.id),
            "outing_id": str(booking_orm.outing.id) if booking_orm.outing else None,
            "activity_info": {
                "costs": {
                    "total_cents": total_cost_cents,
                },
            },
            "survey_info": Survey.from_orm(booking_orm.outing.survey).build_analytics_properties()
            if booking_orm.outing and booking_orm.outing.survey
            else None,
        },
    )


async def _notify_slack_booking_confirmed(
    *,
    booking_orm: BookingOrm,
    account_orm: AccountOrm,
    total_cost_cents: int,
) -> None:
    total_cost_formatted = f"${"{:.2f}".format(total_cost_cents / 100)}"
    reserver_details = booking_orm.reserver_details

    msg = f"Outing Booked for {total_cost_formatted} - "
    elements: list[str] = []

    if len(booking_orm.reservations) > 0:
        places = GooglePlacesUtility()
        rez = await places.get_google_place(place_id=booking_orm.reservations[0].source_id)
        if rez.reservable:
            elements.append("Restaurant Reservation Required")

    if len(booking_orm.activities) > 0:
        if booking_orm.activities[0].source == ActivitySource.EVENTBRITE:
            elements.append("Activity Tickets Required")

    if len(elements) > 0:
        msg += ", ".join(elements)
    else:
        msg += "no action required (probably)"

    try:
        channel_id = SHARED_CONFIG.eave_slack_alerts_bookings_channel_id
        slack_client = eave.stdlib.slack.get_authenticated_eave_system_slack_client()

        if slack_client and channel_id:
            slack_response = await slack_client.chat_postMessage(
                channel=channel_id,
                link_names=True,
                text=msg,
            )

            # TODO: distinguish whether any action on our part is needed for one or both options?
            await slack_client.chat_postMessage(
                channel=channel_id,
                thread_ts=slack_response.get("ts"),
                link_names=True,
                text=dedent(f"""
                    *Account Info*

                    - *Account ID*: `{account_orm.id}`
                    - *Account Email*: `{account_orm.email}`

                    *Payment*

                    - *Total Cost*: {total_cost_formatted}
                    - *Stripe Payment Intent*: {f"https://dashboard.stripe.com/payments/{booking_orm.stripe_payment_intent_reference.stripe_payment_intent_id}" if booking_orm.stripe_payment_intent_reference else None}

                    *Reserver Details*

                    - *First Name*: `{reserver_details.first_name if reserver_details else "UNKNOWN"}`
                    - *Last Name*: `{reserver_details.last_name if reserver_details else "UNKNOWN"}`
                    - *Phone Number*: `{reserver_details.phone_number if reserver_details else "UNKNOWN"}`

                    {"\n".join([
                    f"""*Reservation*

                    - *Source*: {reservation.source}
                    - *Name*: {reservation.name}
                    - *Start Time*: {_pretty_datetime(reservation.start_time_local)}
                    - *Attendees*: {reservation.headcount}
                    - *Booking URL*: {reservation.external_booking_link}
                    """
                        for reservation in booking_orm.reservations
                    ])}

                    {"\n".join([
                    f"""*Activity*

                    - *Source*: {activity.source}
                    - *Name*: {activity.name}
                    - *Start Time*: {_pretty_datetime(activity.start_time_local)}
                    - *Attendees*: {activity.headcount}
                    - *Booking URL*: {activity.external_booking_link}
                    """
                        for activity in booking_orm.activities
                    ])}

                    *Internal Booking ID*: {booking_orm.id}
                    """),
            )
    except Exception as e:
        if SHARED_CONFIG.is_local:
            raise
        else:
            LOGGER.exception(e)


def _fire_booking_confirmation_email(*, booking_orm: BookingOrm, account_orm: AccountOrm) -> None:
    send_booking_confirmation_email(
        to_email=account_orm.email,
        data=BookingConfirmationData(
            booking_date=_pretty_datetime(booking_orm.start_time_local),
            booking_details_url=f"{SHARED_CONFIG.eave_dashboard_base_url_public}/plans/{booking_orm.id}?utm_source=booking-confirmation-email",
            activities=[
                EventItem(
                    name=a.name,
                    time=_pretty_time(a.start_time_local),
                )
                for a in booking_orm.activities
            ],
            restaurants=[
                EventItem(
                    name=r.name,
                    time=_pretty_time(r.start_time_local),
                )
                for r in booking_orm.reservations
            ],
        ),
    )


def _pretty_time(dt: datetime) -> str:
    return dt.strftime("%I:%M%p")


def _pretty_datetime(dt: datetime) -> str:
    suffixed_day = num_with_english_suffix(dt.day)

    minutefmt = ":%M"
    if dt.minute == 0:
        minutefmt = ""

    return dt.strftime(f"%A, %B {suffixed_day} at %-I{minutefmt}%p %Z")
