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
from eave.core.graphql.resolvers.mutations.helpers.create_outing import get_total_cost_cents
from eave.core.graphql.resolvers.mutations.helpers.time_bounds_validator import (
    StartTimeTooLateError,
    StartTimeTooSoonError,
    validate_time_within_bounds_or_exception,
)
from eave.core.graphql.types.booking import (
    Booking,
)
from eave.core.orm.account import AccountOrm
from eave.core.orm.booking import BookingOrm
from eave.core.orm.reserver_details import ReserverDetailsOrm
from eave.core.orm.search_region import SearchRegionOrm
from eave.core.orm.stripe_payment_intent_reference import StripePaymentIntentReferenceOrm
from eave.core.shared.enums import BookingState
from eave.core.shared.errors import ValidationError
from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.logging import LOGGER
from eave.stdlib.util import unwrap


@strawberry.input
class PaymentIntentInput:
    id: str
    client_secret: str


@strawberry.input
class ConfirmBookingInput:
    booking_id: UUID
    payment_intent: PaymentIntentInput | None = strawberry.UNSET


@strawberry.type
class ConfirmBookingSuccess:
    booking: Booking


@strawberry.enum
class ConfirmBookingFailureReason(enum.Enum):
    PAYMENT_REQUIRED = enum.auto()
    BOOKING_NOT_FOUND = enum.auto()
    INVALID_PAYMENT_INTENT = enum.auto()
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

    if booking.outing and booking.outing.survey:
        # TODO: This is messy, consolidate all of these duplicate checks into one place
        # validate outing time still valid to book
        try:
            validate_time_within_bounds_or_exception(
                start_time=booking.outing.survey.start_time_utc, timezone=booking.outing.survey.timezone
            )
        except StartTimeTooSoonError:
            return ConfirmBookingFailure(failure_reason=ConfirmBookingFailureReason.START_TIME_TOO_SOON)
        except StartTimeTooLateError:
            return ConfirmBookingFailure(failure_reason=ConfirmBookingFailureReason.START_TIME_TOO_LATE)

    if input.payment_intent:
        # Even if the cost of the outing is $0, if we were given a payment intent then we will validate it.
        if not input.payment_intent.id or not input.payment_intent.client_secret:
            LOGGER.error("invalid payment intent input")
            # Validates that the fields don't contain empty values.
            return ConfirmBookingFailure(failure_reason=ConfirmBookingFailureReason.INVALID_PAYMENT_INTENT)

        async with database.async_session.begin() as db_session:
            # If a payment intent was given:
            # 1. Confirm it's in the database,
            # 2. Confirm it's for the given booking
            stripe_payment_intent_reference = await StripePaymentIntentReferenceOrm.get_one(
                db_session, account_id=account.id, stripe_payment_intent_id=input.payment_intent.id
            )

        if booking.stripe_payment_intent_reference_id != stripe_payment_intent_reference.id:
            LOGGER.error("given payment intent not for given booking")
            return ConfirmBookingFailure(failure_reason=ConfirmBookingFailureReason.INVALID_PAYMENT_INTENT)

        # Get the given payment intent from the Stripe API
        stripe_payment_intent = await stripe.PaymentIntent.retrieve_async(
            id=input.payment_intent.id,
            # client_secret=input.payment_intent.client_secret,
        )

        # Validate that the payment intent has been authorized, but the funds haven't been captured.
        # This is important because if the payment authorization failed, we shouldn't create the booking.
        if stripe_payment_intent.status not in ["success", "requires_capture"]:
            return ConfirmBookingFailure(failure_reason=ConfirmBookingFailureReason.PAYMENT_REQUIRED)
    else:
        stripe_payment_intent = None
        stripe_payment_intent_reference = None

    # Although we already checked the cost in the `initiate booking` operation,
    # It's important that we double-check it here too, in case the real cost changed.
    # It's not enough to store the pre-calculated cost in the database somewhere, because that can become out of date.
    booking_total_cost_cents = await get_total_cost_cents(booking)

    if booking_total_cost_cents > 0:
        # If the outing costs any money, then:

        # Validate that there is a payment intent.
        if not stripe_payment_intent or not stripe_payment_intent_reference:
            LOGGER.error("No payment intent available")
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
            "booked_outing_id": str(booking.outing.id) if booking.outing else None,
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
    booking: BookingOrm,
    account: AccountOrm,
    reserver_details: ReserverDetailsOrm | None,
    total_cost_cents: int,
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

                    Reserver first name: `{reserver_details.first_name if reserver_details else "UNKNOWN"}`
                    Reserver last name: `{reserver_details.last_name if reserver_details else "UNKNOWN"}`
                    Reserver phone number: `{reserver_details.phone_number if reserver_details else "UNKNOWN"}`

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
                    ])}

                    *Total Cost:* ${"{:.2f}".format(total_cost_cents / 100)}
                    *Stripe Payment Intent ID*: {booking.stripe_payment_intent_reference.stripe_payment_intent_id if booking.stripe_payment_intent_reference else None}
                    """),
            )
    except Exception as e:
        LOGGER.exception(e)
