import enum
from typing import Annotated
from uuid import UUID

import strawberry
import stripe

from eave.core import database
from eave.core.graphql.context import GraphQLContext, log_ctx
from eave.core.graphql.resolvers.mutations.viewer.confirm_booking import (
    perform_post_confirm_actions,
)
from eave.core.graphql.types.activity import ActivityPlan
from eave.core.graphql.types.booking import (
    BookingDetails,
)
from eave.core.graphql.types.itinerary import Itinerary
from eave.core.graphql.types.restaurant import Reservation
from eave.core.graphql.types.stripe import CustomerSession, PaymentIntent
from eave.core.graphql.types.survey import Survey
from eave.core.graphql.validators.time_bounds_validator import start_time_too_far_away, start_time_too_soon
from eave.core.lib.analytics_client import ANALYTICS
from eave.core.lib.event_helpers import resolve_activity_details, resolve_restaurant_details
from eave.core.orm.account import AccountOrm
from eave.core.orm.base import InvalidRecordError
from eave.core.orm.booking import BookingActivityTemplateOrm, BookingOrm, BookingReservationTemplateOrm
from eave.core.orm.outing import OutingOrm
from eave.core.orm.stripe_payment_intent_reference import StripePaymentIntentReferenceOrm
from eave.core.shared.enums import BookingState
from eave.core.shared.errors import ValidationError
from eave.stdlib.logging import LOGGER
from eave.stdlib.util import unwrap


@strawberry.input
class InitiateBookingInput:
    outing_id: UUID
    auto_confirm: bool = False
    payment_method_id: str | None = None


@strawberry.type
class InitiateBookingSuccess:
    booking: BookingDetails
    payment_intent: PaymentIntent | None
    customer_session: CustomerSession | None


@strawberry.enum
class InitiateBookingFailureReason(enum.Enum):
    BOOKING_ALREADY_CONFIRMED = enum.auto()
    PAYMENT_INTENT_FAILED = enum.auto()
    VALIDATION_ERRORS = enum.auto()
    START_TIME_TOO_SOON = enum.auto()
    START_TIME_TOO_LATE = enum.auto()


@strawberry.type
class InitiateBookingFailure:
    failure_reason: InitiateBookingFailureReason
    validation_errors: list[ValidationError] | None = None


InitiateBookingResult = Annotated[
    InitiateBookingSuccess | InitiateBookingFailure, strawberry.union("InitiateBookingResult")
]


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

    if start_time_too_soon(start_time=outing_orm.start_time_utc, timezone=outing_orm.timezone):
        return InitiateBookingFailure(failure_reason=InitiateBookingFailureReason.START_TIME_TOO_SOON)

    if start_time_too_far_away(start_time=outing_orm.start_time_utc, timezone=outing_orm.timezone):
        return InitiateBookingFailure(failure_reason=InitiateBookingFailureReason.START_TIME_TOO_LATE)

    try:
        async with database.async_session.begin() as db_session:
            # If a booking with account and outing ID already exists, use it.
            # This prevents us from creating a bunch of duplicate bookings with Initiated state.
            booking_orm = next((b for b in account_orm.bookings if b.outing_id == input.outing_id), None)

            if booking_orm:
                if booking_orm.state == BookingState.CONFIRMED:
                    # TODO: It would be nice if this redirected to the "booking confirmed" page.
                    return InitiateBookingFailure(failure_reason=InitiateBookingFailureReason.BOOKING_ALREADY_CONFIRMED)
            else:
                default_reserver_details = account_orm.get_default_reserver_details()

                booking_orm = BookingOrm(
                    db_session,
                    accounts=[account_orm],
                    reserver_details=default_reserver_details,
                    outing=outing_orm,
                    stripe_payment_intent_reference=None,  # Not created yet
                    state=BookingState.INITIATED,
                )

            itinerary = BookingDetails(
                id=booking_orm.id,  # Warning: This is NULL until the Booking object is persisted!
                activity_plan=None,
                reservation=None,
                state=booking_orm.state,
                survey=None,
            )

            if len(outing_orm.activities) > 0:
                outing_activity_orm = outing_orm.activities[0]  # We only support one activity currently.
                activity = await resolve_activity_details(
                    source=outing_activity_orm.source,
                    source_id=outing_activity_orm.source_id,
                    survey=outing_orm.survey,
                )

                if activity:
                    booking_activity_orm = BookingActivityTemplateOrm(
                        db_session,
                        booking=booking_orm,
                        source=outing_activity_orm.source,
                        source_id=outing_activity_orm.source_id,
                        name=activity.name,
                        start_time_utc=outing_activity_orm.start_time_utc,
                        timezone=outing_activity_orm.timezone,
                        headcount=outing_activity_orm.headcount,
                        external_booking_link=activity.website_uri,
                        address=activity.venue.location.address.to_address(),
                        coordinates=activity.venue.location.coordinates,
                        photo_uri=activity.photos.cover_photo.src if activity.photos.cover_photo else None,
                    )

                    booking_orm.activities = [booking_activity_orm]

                    itinerary.activity_plan = ActivityPlan(
                        activity=activity,
                        start_time=booking_activity_orm.start_time_local,
                        headcount=booking_activity_orm.headcount,
                    )

            if len(outing_orm.reservations) > 0:
                reservation_orm = outing_orm.reservations[0]  # We only support 1 reservation right now
                restaurant = await resolve_restaurant_details(
                    source=reservation_orm.source,
                    source_id=reservation_orm.source_id,
                )

                if restaurant:
                    booking_reservation_orm = BookingReservationTemplateOrm(
                        db_session,
                        booking=booking_orm,
                        source=reservation_orm.source,
                        source_id=reservation_orm.source_id,
                        name=restaurant.name,
                        start_time_utc=reservation_orm.start_time_utc,
                        timezone=reservation_orm.timezone,
                        headcount=reservation_orm.headcount,
                        external_booking_link=restaurant.website_uri,
                        address=restaurant.location.address.to_address(),
                        coordinates=restaurant.location.coordinates,
                        photo_uri=restaurant.photos.cover_photo.src if restaurant.photos.cover_photo else None,
                    )

                    booking_orm.reservations = [booking_reservation_orm]

                    itinerary.reservation = Reservation(
                        arrival_time=booking_reservation_orm.start_time_local,
                        headcount=booking_reservation_orm.headcount,
                        restaurant=restaurant,
                    )

        payment_due_cents = itinerary.calculate_payment_due_breakdown().calculate_total_cost_cents()

        if payment_due_cents > 0:
            if not account_orm.stripe_customer_id:
                stripe_customer = await stripe.Customer.create_async(
                    email=account_orm.email,
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

            stripe_payment_create_params: stripe.PaymentIntent.CreateParams = {
                "currency": "usd",
                "amount": payment_due_cents,
                "capture_method": "manual",
                "receipt_email": account_orm.email,
                "setup_future_usage": "on_session",
                "customer": account_orm.stripe_customer_id,
                "metadata": {
                    "vivial_booking_id": str(booking_orm.id),
                },
            }

            if input.auto_confirm:
                stripe_payment_create_params.update(
                    {
                        # Note: this is necessary because we have some payment methods enabled in the dashboard that require
                        # redirects, but currently we only accept credit cards, which do not require a redirect.
                        # Without this, Stripe won't allow auto-confirm.
                        "automatic_payment_methods": {
                            "enabled": True,
                            "allow_redirects": "never",
                        },
                        "confirm": True,
                    }
                )

            if input.payment_method_id:
                stripe_payment_create_params.update(
                    {
                        "payment_method": input.payment_method_id,
                    }
                )

            stripe_payment_intent = await stripe.PaymentIntent.create_async(**stripe_payment_create_params)

            if not stripe_payment_intent.client_secret:
                LOGGER.error("Missing client secret from Stripe Payment Intent response", log_ctx(info.context))
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

                db_session.add(booking_orm)  # Add the existing booking_orm to this session so it can be updated.
                booking_orm.stripe_payment_intent_reference = stripe_payment_intent_reference_orm

            graphql_payment_intent = PaymentIntent(
                id=stripe_payment_intent.id, client_secret=stripe_payment_intent.client_secret
            )

            stripe_customer_session = await stripe.CustomerSession.create_async(
                customer=account_orm.stripe_customer_id,
                components={
                    "payment_element": {
                        "enabled": True,
                        "features": {
                            # These two `payment_method_save` options will add a checkbox to the payment form to save the card.
                            # Although with our current implementation, the card is always saved anyways.
                            # "payment_method_save": "enabled",
                            # "payment_method_save_usage": "on_session",
                            "payment_method_redisplay": "enabled",
                        },
                    },
                },
            )

            graphql_customer_session = CustomerSession(client_secret=stripe_customer_session.client_secret)

        else:
            graphql_payment_intent = None
            graphql_customer_session = None

        if input.auto_confirm:
            async with database.async_session.begin() as db_session:
                db_session.add(booking_orm)

                if itinerary.has_bookable_components:
                    booking_orm.state = BookingState.CONFIRMED
                else:
                    booking_orm.state = BookingState.BOOKED

    except InvalidRecordError as e:
        LOGGER.exception(e, log_ctx(info.context))
        return InitiateBookingFailure(
            failure_reason=InitiateBookingFailureReason.VALIDATION_ERRORS, validation_errors=e.validation_errors
        )

    # Update the state in case it changed in the logic above
    itinerary.state = booking_orm.state
    itinerary.id = booking_orm.id

    if input.auto_confirm:
        await perform_post_confirm_actions(
            booking_orm=booking_orm,
            account_orm=account_orm,
            visitor_id=visitor_id,
            itinerary=itinerary,
        )

    else:
        try:
            _fire_analytics_booking_initiated(
                booking=booking_orm,
                itinerary=itinerary,
                account_id=account_orm.id,
                visitor_id=visitor_id,
            )
        except Exception as e:
            LOGGER.exception(e)

    return InitiateBookingSuccess(
        booking=itinerary,
        payment_intent=graphql_payment_intent,
        customer_session=graphql_customer_session,
    )


def _fire_analytics_booking_initiated(
    *,
    booking: BookingOrm,
    itinerary: Itinerary,
    account_id: UUID,
    visitor_id: str | None,
) -> None:
    ANALYTICS.track(
        event_name="booking_initiated",
        account_id=account_id,
        visitor_id=visitor_id,
        extra_properties={
            "booking_id": str(booking.id),
            "outing_id": str(booking.outing.id) if booking.outing else None,
            "payment_breakdown": itinerary.calculate_payment_due_breakdown().build_analytics_properties(),
            "restaurant_info": itinerary.reservation.build_analytics_properties() if itinerary.reservation else None,
            "activity_info": itinerary.activity_plan.build_analytics_properties() if itinerary.activity_plan else None,
            "survey_info": Survey.from_orm(booking.outing.survey).build_analytics_properties()
            if booking.outing and booking.outing.survey
            else None,
        },
    )
