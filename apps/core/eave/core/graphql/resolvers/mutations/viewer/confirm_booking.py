import enum
from datetime import datetime
from textwrap import dedent
from typing import Annotated
from uuid import UUID

from google.maps.places import PlacesAsyncClient
import strawberry
import stripe

from eave.core.lib.google_places import get_google_place, get_google_places_activity
import eave.stdlib.slack
from eave.core import database
from eave.core.analytics import ANALYTICS
from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.resolvers.mutations.helpers.create_outing import get_total_cost_cents
from eave.core.graphql.types.booking import (
    Booking,
)
from eave.core.graphql.validators.time_bounds_validator import (
    start_time_too_far_away,
    start_time_too_soon,
)
from eave.core.orm.account import AccountOrm
from eave.core.orm.booking import BookingOrm
from eave.core.orm.reserver_details import ReserverDetailsOrm
from eave.core.orm.search_region import SearchRegionOrm
from eave.core.shared.enums import ActivitySource, BookingState
from eave.core.shared.errors import ValidationError
from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.logging import LOGGER
from eave.stdlib.util import unwrap


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
        account = await AccountOrm.get_one(db_session, account_id)
        # It's important that when getting the booking, we use BOTH the account ID and booking ID.
        # Otherwise, it would be possible to confirm any booking, even ones you don't own.
        booking = account.get_booking(booking_id=input.booking_id)

    if not booking:
        return ConfirmBookingFailure(failure_reason=ConfirmBookingFailureReason.BOOKING_NOT_FOUND)

    if booking.state != BookingState.INITIATED:
        # If this booking was already confirmed, then just return the success state,
        # so we don't try to charge their card again and stuff.
        return ConfirmBookingSuccess(
            booking=Booking.from_orm(booking),
        )

    if start_time_too_soon(start_time=booking.start_time_utc, timezone=booking.timezone):
        return ConfirmBookingFailure(failure_reason=ConfirmBookingFailureReason.START_TIME_TOO_SOON)

    if start_time_too_far_away(start_time=booking.start_time_utc, timezone=booking.timezone):
        return ConfirmBookingFailure(failure_reason=ConfirmBookingFailureReason.START_TIME_TOO_LATE)

    if booking.stripe_payment_intent_reference:
        # Get the given payment intent from the Stripe API
        stripe_payment_intent = await stripe.PaymentIntent.retrieve_async(
            id=booking.stripe_payment_intent_reference.stripe_payment_intent_id,
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
    booking_total_cost_cents = await get_total_cost_cents(booking)

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
        db_session.add(booking)

        if booking.reserver_details is None and len(account.reserver_details) > 0:
            # Hacky way to make sure some reserver details are set.
            # There is still a possibility that they won't be, though.
            booking.reserver_details = account.reserver_details[0]

        booking.state = BookingState.CONFIRMED

    # TODO: Move this into an offline queue
    await _notify_slack(
        booking=booking,
        account=account,
        reserver_details=booking.reserver_details,
        total_cost_cents=booking_total_cost_cents,
    )

    ANALYTICS.track(
        event_name="booking_complete",
        account_id=account_id,
        visitor_id=visitor_id,
        extra_properties={
            "booking_id": str(booking.id),
            "outing_id": str(booking.outing.id) if booking.outing else None,
            "activity_info": {
                "costs": {
                    "total_cents": booking_total_cost_cents,
                },
            },
            "survey_info": {
                "headcount": booking.outing.survey.headcount if booking.outing and booking.outing.survey else None,
                "start_time": booking.outing.survey.start_time_local.isoformat()
                if booking.outing and booking.outing.survey
                else None,
                "regions": [
                    SearchRegionOrm.one_or_exception(search_region_id=region).name
                    for region in booking.outing.survey.search_area_ids
                ]
                if booking.outing and booking.outing.survey
                else None,
                "budget": booking.outing.survey.budget if booking.outing and booking.outing.survey else None,
            },
        },
    )

    return ConfirmBookingSuccess(
        booking=Booking.from_orm(booking),
    )


async def _notify_slack(
    *,
    booking: BookingOrm,
    account: AccountOrm,
    reserver_details: ReserverDetailsOrm | None,
    total_cost_cents: int,
) -> None:
    total_cost_formatted = f"${"{:.2f}".format(total_cost_cents / 100)}"

    msg = f"Outing Booked for {total_cost_formatted} - "
    elements: list[str] = []

    if len(booking.reservations) > 0:
        rez = await get_google_place(PlacesAsyncClient(), place_id=booking.reservations[0].source_id)
        if rez.reservable:
            elements.append("Restaurant Reservation Required")

    if len(booking.activities) > 0:
        if booking.activities[0].source == ActivitySource.EVENTBRITE:
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
                text=msg,
            )

            # TODO: distinguish whether any action on our part is needed for one or both options?
            await slack_client.chat_postMessage(
                channel=channel_id,
                thread_ts=slack_response.get("ts"),
                link_names=True,
                text=dedent(f"""
                    *Account Info*

                    - *Account ID*: `{account.id}`
                    - *Account Email*: `{account.email}`

                    *Payment*

                    - *Total Cost*: {total_cost_formatted}
                    - *Stripe Payment Intent*: {f"https://dashboard.stripe.com/payments/{booking.stripe_payment_intent_reference.stripe_payment_intent_id}" if booking.stripe_payment_intent_reference else None}

                    *Reserver Details*

                    - *First Name*: `{reserver_details.first_name if reserver_details else "UNKNOWN"}`
                    - *Last Name*: `{reserver_details.last_name if reserver_details else "UNKNOWN"}`
                    - *Phone Number*: `{reserver_details.phone_number if reserver_details else "UNKNOWN"}`

                    {"\n".join([
                    f"""*Reservation*

                    - *Source*: {reservation.source}
                    - *Name*: {reservation.name}
                    - *Start Time*: {_pretty_time(reservation.start_time_local)}
                    - *Attendees*: {reservation.headcount}
                    - *Booking URL*: {reservation.external_booking_link}
                    """
                        for reservation in booking.reservations
                    ])}

                    {"\n".join([
                    f"""*Activity*

                    - *Source*: {activity.source}
                    - *Name*: {activity.name}
                    - *Start Time*: {_pretty_time(activity.start_time_local)}
                    - *Attendees*: {activity.headcount}
                    - *Booking URL*: {activity.external_booking_link}
                    """
                        for activity in booking.activities
                    ])}

                    *Internal Booking ID*: {booking.id}

                    @customer-support
                    """),
            )
    except Exception as e:
        LOGGER.exception(e)


def _pretty_time(dt: datetime) -> str:
    return dt.strftime("%A, %B %d at %I:%M%p %Z")
