import enum
from textwrap import dedent
from typing import Annotated
from uuid import UUID

import strawberry
import stripe
from attr import dataclass
from google.maps.places_v1 import PlacesAsyncClient

import eave.stdlib.slack
from eave.core import database
from eave.core.analytics import ANALYTICS
from eave.core.config import CORE_API_APP_CONFIG
from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.resolvers.mutations.helpers.time_bounds_validator import (
    StartTimeTooLateError,
    StartTimeTooSoonError,
    validate_time_within_bounds_or_exception,
)
from eave.core.graphql.types.booking import (
    Booking,
)
from eave.core.lib.google_places import get_google_place, photos_from_google_place
from eave.core.orm.account import AccountOrm
from eave.core.orm.activity import ActivityOrm
from eave.core.orm.base import InvalidRecordError
from eave.core.orm.booking import BookingActivityTemplateOrm, BookingOrm, BookingReservationTemplateOrm
from eave.core.orm.outing import OutingOrm
from eave.core.orm.reserver_details import ReserverDetailsOrm
from eave.core.shared.address import Address
from eave.core.shared.enums import ActivitySource, RestaurantSource
from eave.core.shared.errors import ValidationError
from eave.core.shared.geo import GeoPoint
from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.eventbrite.client import EventbriteClient, GetEventQuery
from eave.stdlib.eventbrite.models.expansions import Expansion
from eave.stdlib.logging import LOGGER
from eave.stdlib.util import unwrap


@dataclass
class BookingTemplates:
    activities: list[BookingActivityTemplateOrm]
    reservations: list[BookingReservationTemplateOrm]


@dataclass
class EventDetails:
    name: str
    coordinates: GeoPoint
    address: Address
    uri: str
    photo_uri: str | None


async def _get_event_details(
    source: ActivitySource | RestaurantSource,
    source_id: str,
) -> EventDetails:
    places_client = PlacesAsyncClient()
    eventbrite_client = EventbriteClient(api_key=CORE_API_APP_CONFIG.eventbrite_api_key)

    name: str | None = None
    address: Address | None = None
    coordinates: GeoPoint | None = None
    booking_uri: str | None = None
    photo_uri: str | None = None

    match source:
        case ActivitySource.INTERNAL:
            async with database.async_session.begin() as db_session:
                details = await ActivityOrm.get_one(
                    db_session,
                    UUID(source_id),
                )
            name = details.title
            coordinates = details.coordinates_to_geopoint()
            address = Address(
                address1=details.address.address1,
                address2=details.address.address2,
                city=details.address.city,
                state=details.address.state,
                zip=details.address.zip,
                country=details.address.country,
            )
            booking_uri = details.booking_url

        case ActivitySource.GOOGLE_PLACES | RestaurantSource.GOOGLE_PLACES:
            details = await get_google_place(
                places_client=places_client,
                place_id=source_id,
            )

            photos = await photos_from_google_place(places_client, place=details)
            photo_uri = photos.cover_photo_uri

            name = details.display_name.text
            booking_uri = details.websiteUri

            address = Address(
                country=next(
                    (component.shortText for component in details.addressComponents if "country" in component.types),
                    "US",
                ),
                state=next(
                    (
                        component.shortText
                        for component in details.addressComponents
                        if "administrative_area_level_1" in component.types
                    ),
                    "",
                ),
                city=next(
                    (component.longText for component in details.addressComponents if "locality" in component.types),
                    "",
                ),
                zip=next(
                    (component.longText for component in details.addressComponents if "postal_code" in component.types),
                    "",
                ),
                address1=next(
                    (
                        component.longText
                        for component in details.addressComponents
                        if "street_address" in component.types
                    ),
                    None,
                )
                or " ".join(  # fallback to constructing address from more granular components
                    [
                        next(
                            (
                                component.longText
                                for component in details.addressComponents
                                if "street_number" in component.types
                            ),
                            "",
                        ),
                        next(
                            (
                                component.longText
                                for component in details.addressComponents
                                if "route" in component.types
                            ),
                            "",
                        ),
                    ]
                ),
                address2=next(
                    (component.longText for component in details.addressComponents if "subpremise" in component.types),
                    None,
                ),
            )

            coordinates = GeoPoint(
                lat=details.location.latitude,
                lon=details.location.longitude,
            )

        case ActivitySource.EVENTBRITE:
            details = await eventbrite_client.get_event_by_id(
                event_id=source_id,
                query=GetEventQuery(expand=Expansion.all()),
            )
            name = details.get("name", {}).get("text")
            booking_uri = details.get("url")
            if venue := details.get("venue"):
                lat = venue.get("latitude")
                lon = venue.get("longitude")

                if lat is not None and lon is not None:
                    coordinates = GeoPoint(
                        lat=float(lat),
                        lon=float(lon),
                    )

                if venue_address := venue.get("address"):
                    address = Address(
                        address1=venue_address.get("address_1"),
                        address2=venue_address.get("address_2"),
                        city=venue_address.get("city"),
                        state=venue_address.get("region"),
                        zip=venue_address.get("postal_code"),
                        country=venue_address.get("country"),
                    )
            if logo := details.get("logo"):
                photo_uri = logo.get("original", {}).get("url")

    assert name is not None
    assert coordinates is not None
    assert address is not None
    assert booking_uri is not None

    return EventDetails(
        name=name,
        coordinates=coordinates,
        address=address,
        uri=booking_uri,
        photo_uri=photo_uri,
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

            reserver_details = await ReserverDetailsOrm.get_one(db_session, input.reserver_details_id)
            account = await AccountOrm.get_one(db_session, account_id)

            booking = BookingOrm(
                reserver_details=reserver_details,
                stripe_payment_intent_reference=stripe_payment_intent_reference_orm,
            )

            db_session.add(booking)
            booking.accounts = [account]

            for activity in outing.activities:
                details = await _get_event_details(
                    source=activity.source,
                    source_id=activity.source_id,
                )

                booking.activities.append(
                    BookingActivityTemplateOrm(
                        booking=booking,
                        source=activity.source,
                        source_id=activity.source_id,
                        name=details.name,
                        start_time_utc=activity.start_time_utc,
                        timezone=activity.timezone,
                        headcount=activity.headcount,
                        external_booking_link=details.uri,
                        address=details.address,
                        coordinates=details.coordinates,
                        photo_uri=details.photo_uri,
                    )
                )

            for reservation in outing.reservations:
                details = await _get_event_details(
                    source=reservation.source,
                    source_id=reservation.source_id,
                )

                booking.reservations.append(
                    BookingReservationTemplateOrm(
                        booking=booking,
                        source=reservation.source,
                        source_id=reservation.source_id,
                        name=details.name,
                        start_time_utc=reservation.start_time_utc,
                        timezone=reservation.timezone,
                        headcount=reservation.headcount,
                        external_booking_link=details.uri,
                        address=details.address,
                        coordinates=details.coordinates,
                        photo_uri=details.photo_uri,
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
