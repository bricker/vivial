import enum
from textwrap import dedent
from typing import Annotated
from uuid import UUID

import strawberry
import stripe

from eave.core.shared.enums import BookingState
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
from eave.core.lib.event_helpers import get_activity, get_restaurant
from eave.core.orm.account import AccountOrm
from eave.core.orm.base import InvalidRecordError
from eave.core.orm.booking import BookingActivityTemplateOrm, BookingOrm, BookingReservationTemplateOrm
from eave.core.orm.outing import OutingOrm
from eave.core.orm.reserver_details import ReserverDetailsOrm
from eave.core.orm.stripe_payment_intent_reference import StripePaymentIntentReferenceOrm
from eave.core.shared.errors import ValidationError
from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.logging import LOGGER
from eave.stdlib.util import unwrap


@strawberry.input
class UpdateBookingInput:
    booking_id: UUID
    reserver_details_id: UUID | None = strawberry.UNSET


@strawberry.type
class UpdateBookingSuccess:
    booking: Booking


@strawberry.enum
class UpdateBookingFailureReason(enum.Enum):
    BOOKING_NOT_FOUND = enum.auto()
    VALIDATION_ERRORS = enum.auto()


@strawberry.type
class UpdateBookingFailure:
    failure_reason: UpdateBookingFailureReason
    validation_errors: list[ValidationError] | None = None


UpdateBookingResult = Annotated[UpdateBookingSuccess | UpdateBookingFailure, strawberry.union("UpdateBookingResult")]


async def update_booking_mutation(
    *,
    info: strawberry.Info[GraphQLContext],
    input: UpdateBookingInput,
) -> UpdateBookingResult:
    account_id = unwrap(info.context.get("authenticated_account_id"))

    async with database.async_session.begin() as db_session:
        account = await AccountOrm.get_one(db_session, account_id)

        # It's important that when getting the booking, we use BOTH the account ID and booking ID.
        # Otherwise, it would be possible to confirm any booking, even ones you don't own.
        booking = account.get_booking(booking_id=input.booking_id)

        if not booking:
            return UpdateBookingFailure(failure_reason=UpdateBookingFailureReason.BOOKING_NOT_FOUND)

        if input.reserver_details_id:
            # It's also important that we make sure the given reserver details ID belongs to the viewer account.
            reserver_details = await ReserverDetailsOrm.get_one(db_session, account_id=account_id, uid=input.reserver_details_id)
            booking.reserver_details = reserver_details

    return UpdateBookingSuccess(
        booking=Booking.from_orm(booking),
    )


async def _notify_slack(
    booking: BookingOrm,
    account: AccountOrm,
    reserver_details: ReserverDetailsOrm,
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
                    ])}

                    *Total Cost:* ${"{:.2f}".format(total_cost_cents / 100)}
                    *Stripe Payment Intent ID*: {booking.stripe_payment_intent_reference.stripe_payment_intent_id if booking.stripe_payment_intent_reference else None}
                    """),
            )
    except Exception as e:
        LOGGER.exception(e)
