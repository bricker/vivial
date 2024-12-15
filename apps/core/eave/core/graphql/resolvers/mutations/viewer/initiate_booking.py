import enum
from textwrap import dedent
from typing import Annotated
from uuid import UUID

import strawberry
import stripe

from eave.core.graphql.types.payment_intent import PaymentIntent
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
class InitiateBookingInput:
    outing_id: UUID


@strawberry.type
class InitiateBookingSuccess:
    booking: Booking
    payment_intent: PaymentIntent | None


@strawberry.enum
class InitiateBookingFailureReason(enum.Enum):
    START_TIME_TOO_SOON = enum.auto()
    START_TIME_TOO_LATE = enum.auto()
    PAYMENT_INTENT_FAILED = enum.auto()
    VALIDATION_ERRORS = enum.auto()


@strawberry.type
class InitiateBookingFailure:
    failure_reason: InitiateBookingFailureReason
    validation_errors: list[ValidationError] | None = None


InitiateBookingResult = Annotated[InitiateBookingSuccess | InitiateBookingFailure, strawberry.union("InitiateBookingResult")]


async def initiate_booking_mutation(
    *,
    info: strawberry.Info[GraphQLContext],
    input: InitiateBookingInput,
) -> InitiateBookingResult:
    account_id = unwrap(info.context.get("authenticated_account_id"))
    visitor_id = info.context.get("visitor_id")

    async with database.async_session.begin() as db_session:
        account_orm = await AccountOrm.get_one(db_session, account_id)
        outing_orm = await OutingOrm.get_one(db_session, input.outing_id)
        survey_orm = outing_orm.survey

    # validate outing time still valid to book
    try:
        validate_time_within_bounds_or_exception(start_time=survey_orm.start_time_utc, timezone=survey_orm.timezone)
    except StartTimeTooSoonError:
        return InitiateBookingFailure(failure_reason=InitiateBookingFailureReason.START_TIME_TOO_SOON)
    except StartTimeTooLateError:
        return InitiateBookingFailure(failure_reason=InitiateBookingFailureReason.START_TIME_TOO_LATE)

    try:
        outing_total_cost_cents = 0

        async with database.async_session.begin() as db_session:
            booking = BookingOrm(
                db_session,
                accounts=[account_orm],
                reserver_details=None, # At this point, the client hasn't given us this information.
                survey=survey_orm,
                stripe_payment_intent_reference=None, # Not created yet
                state=BookingState.INITIATED,
            )

            for activity_orm in outing_orm.activities:
                activity = await get_activity(source=activity_orm.source, source_id=activity_orm.source_id)

                if activity:
                    if activity.ticket_info:
                        outing_total_cost_cents += activity.ticket_info.cost_breakdown.total_cost_cents_internal * activity_orm.headcount

                    booking.activities.append(
                        BookingActivityTemplateOrm(
                            db_session,
                            booking=booking,
                            source=activity_orm.source,
                            source_id=activity_orm.source_id,
                            name=activity.name,
                            start_time_utc=activity_orm.start_time_utc,
                            timezone=activity_orm.timezone,
                            headcount=activity_orm.headcount,
                            external_booking_link=activity.website_uri,
                            address=activity.venue.location.address.to_address(),
                            coordinates=activity.venue.location.coordinates,
                            photo_uri=activity.photos.cover_photo.src if activity.photos.cover_photo else None,
                        )
                    )

            for reservation_orm in outing_orm.reservations:
                reservation = await get_restaurant(
                    source=reservation_orm.source,
                    source_id=reservation_orm.source_id,
                )

                booking.reservations.append(
                    BookingReservationTemplateOrm(
                        db_session,
                        booking=booking,
                        source=reservation_orm.source,
                        source_id=reservation_orm.source_id,
                        name=reservation.name,
                        start_time_utc=reservation_orm.start_time_utc,
                        timezone=reservation_orm.timezone,
                        headcount=reservation_orm.headcount,
                        external_booking_link=reservation.website_uri,
                        address=reservation.location.address.to_address(),
                        coordinates=reservation.location.coordinates,
                        photo_uri=reservation.photos.cover_photo.src if reservation.photos.cover_photo else None,
                    )
                )

        if outing_total_cost_cents > 0:
            if account_orm.stripe_customer_id is None:
                stripe_customer = await stripe.Customer.create_async(
                    email=account_orm.email,
                    source="vivial-core-api",
                    metadata={
                        "vivial_account_id": str(account_orm.id),
                    },
                )

                async with database.async_session.begin() as db_session:
                    # We do this in a different session than the one fetching outing_orm because fetching outing_orm loads the
                    # associated account, which may be the same as the authed account, in which case the session already has the
                    # account attached and an error is thrown.
                    db_session.add(account_orm)
                    account_orm.stripe_customer_id = stripe_customer.id

            stripe_payment_intent = await stripe.PaymentIntent.create_async(
                currency="usd",
                amount=outing_total_cost_cents,
                capture_method="manual",
                receipt_email=account_orm.email,
                setup_future_usage="on_session",
                customer=account_orm.stripe_customer_id,
                metadata={
                    "vivial_outing_id": str(outing_orm.id),
                },
            )

            if not stripe_payment_intent.client_secret:
                LOGGER.error("Missing client secret from Stripe Payment Intent response")
                return InitiateBookingFailure(failure_reason=InitiateBookingFailureReason.PAYMENT_INTENT_FAILED)

            async with database.async_session.begin() as db_session:
                # Create the payment intent reference in our database.
                # Warning: `client_secret` is a sensitive value and shouldn't be logged or stored.
                # https://docs.stripe.com/api/payment_intents/object#payment_intent_object-client_secret
                stripe_payment_intent_reference_orm = StripePaymentIntentReferenceOrm(
                    db_session,
                    account=account_orm,
                    stripe_payment_intent_id=stripe_payment_intent.id,
                )

                db_session.add(booking)
                booking.stripe_payment_intent_reference = stripe_payment_intent_reference_orm

            graphql_payment_intent = PaymentIntent(id=stripe_payment_intent.id, client_secret=stripe_payment_intent.client_secret)
        else:
            graphql_payment_intent = None

    except InvalidRecordError as e:
        LOGGER.exception(e)
        return InitiateBookingFailure(
            failure_reason=InitiateBookingFailureReason.VALIDATION_ERRORS, validation_errors=e.validation_errors
        )

    ANALYTICS.track(
        event_name="booking initiated",
        account_id=account_orm.id,
        visitor_id=visitor_id,
        extra_properties={
            "booking_id": str(booking.id),
            "total_cost_cents": outing_total_cost_cents,
            "booking_constraints": {
                "headcount": survey_orm.headcount,
                "budget": survey_orm.budget,
                "search_areas": survey_orm.search_area_ids,
            }
        },
    )

    return InitiateBookingSuccess(
        booking=Booking.from_orm(booking),
        payment_intent=graphql_payment_intent,
    )
