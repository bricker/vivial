import enum
from typing import Annotated
from uuid import UUID

import strawberry
import stripe

from eave.core import database
from eave.core.analytics import ANALYTICS
from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.types.booking import (
    BookingDetails,
)
from eave.core.graphql.types.payment_intent import PaymentIntent
from eave.core.graphql.types.pricing import CostBreakdown
from eave.core.graphql.types.survey import Survey
from eave.core.graphql.validators.time_bounds_validator import start_time_too_far_away, start_time_too_soon
from eave.core.lib.address import format_address
from eave.core.lib.event_helpers import get_activity, get_restaurant
from eave.core.orm.account import AccountOrm
from eave.core.orm.base import InvalidRecordError
from eave.core.orm.booking import BookingActivityTemplateOrm, BookingOrm, BookingReservationTemplateOrm
from eave.core.orm.outing import OutingOrm
from eave.core.orm.search_region import SearchRegionOrm
from eave.core.orm.stripe_payment_intent_reference import StripePaymentIntentReferenceOrm
from eave.core.shared.enums import BookingState
from eave.core.shared.errors import ValidationError
from eave.stdlib.logging import LOGGER
from eave.stdlib.util import unwrap


@strawberry.input
class InitiateBookingInput:
    outing_id: UUID


@strawberry.type
class InitiateBookingSuccess:
    booking: BookingDetails
    payment_intent: PaymentIntent | None


@strawberry.enum
class InitiateBookingFailureReason(enum.Enum):
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
        return InitiateBookingFailure(failure_reason=InitiateBookingFailureReason.START_TIME_TOO_SOON)

    booking_details_cost_breakdown = CostBreakdown()
    booking_details_activity = None
    booking_details_activity_start_time = None
    booking_details_restaurant = None
    booking_details_restaurant_arrival_time = None

    try:
        async with database.async_session.begin() as db_session:
            booking = BookingOrm(
                db_session,
                accounts=[account_orm],
                reserver_details=None,  # At this point, the client hasn't given us this information.
                outing=outing_orm,
                stripe_payment_intent_reference=None,  # Not created yet
                state=BookingState.INITIATED,
            )

            for activity_orm in outing_orm.activities:
                activity = await get_activity(source=activity_orm.source, source_id=activity_orm.source_id)

                if activity:
                    if not booking_details_activity:
                        booking_details_activity = activity
                        booking_details_activity_start_time = activity_orm.start_time_local

                    if activity.ticket_info:
                        booking_details_cost_breakdown += activity.ticket_info.cost_breakdown * activity_orm.headcount

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

                if not booking_details_restaurant:
                    booking_details_restaurant = reservation
                    booking_details_restaurant_arrival_time = reservation_orm.start_time_local

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

        if booking_details_cost_breakdown.total_cost_cents_internal > 0:
            if account_orm.stripe_customer_id is None:
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

            stripe_payment_intent = await stripe.PaymentIntent.create_async(
                currency="usd",
                amount=booking_details_cost_breakdown.total_cost_cents_internal,
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

            graphql_payment_intent = PaymentIntent(
                id=stripe_payment_intent.id, client_secret=stripe_payment_intent.client_secret
            )
        else:
            graphql_payment_intent = None

    except InvalidRecordError as e:
        LOGGER.exception(e)
        return InitiateBookingFailure(
            failure_reason=InitiateBookingFailureReason.VALIDATION_ERRORS, validation_errors=e.validation_errors
        )

    ANALYTICS.track(
        event_name="booking_initiated",
        account_id=account_id,
        visitor_id=visitor_id,
        extra_properties={
            "booking_id": str(booking.id),
            "outing_id": str(input.outing_id),
            "restaurant_info": {
                "start_time": booking_details_restaurant_arrival_time.isoformat()
                if booking_details_restaurant_arrival_time
                else None,
                "category": booking_details_restaurant.primary_type_name if booking_details_restaurant else None,
                "accepts_reservations": booking_details_restaurant.reservable if booking_details_restaurant else None,
                "address": format_address(booking_details_restaurant.location.address.to_address(), singleline=True)
                if booking_details_restaurant
                else None,
            },
            "activity_info": {
                "start_time": booking_details_activity_start_time.isoformat()
                if booking_details_activity_start_time
                else None,
                "category": booking_details_activity.category_group.name
                if booking_details_activity and booking_details_activity.category_group
                else None,
                "costs": {
                    "total_cents": booking_details_cost_breakdown.total_cost_cents_internal,
                    "fees_cents": booking_details_cost_breakdown.fee_cents,
                    "tax_cents": booking_details_cost_breakdown.tax_cents,
                },
                "address": format_address(booking_details_activity.venue.location.address.to_address(), singleline=True)
                if booking_details_activity
                else None,
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

    return InitiateBookingSuccess(
        booking=BookingDetails(
            id=booking.id,  # Warning: This is NULL until the Booking object is persisted!
            survey=Survey.from_orm(booking.outing.survey) if booking.outing and booking.outing.survey else None,
            cost_breakdown=booking_details_cost_breakdown,
            activity=booking_details_activity,
            activity_start_time=booking_details_activity_start_time,
            restaurant=booking_details_restaurant,
            restaurant_arrival_time=booking_details_restaurant_arrival_time,
            driving_time=None,  # TODO: can we fill this in?
        ),
        payment_intent=graphql_payment_intent,
    )
