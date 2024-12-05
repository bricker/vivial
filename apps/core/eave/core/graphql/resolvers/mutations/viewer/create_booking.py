import enum
from textwrap import dedent
from typing import Annotated
from uuid import UUID

import strawberry
from attr import dataclass
from google.maps.places_v1 import PlacesAsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

import eave.stdlib.slack
from eave.core import database
from eave.core.analytics import ANALYTICS
from eave.core.config import CORE_API_APP_CONFIG
from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.resolvers.mutations.helpers.planner import get_place
from eave.core.graphql.types.booking import (
    Booking,
)
from eave.core.lib.event_helpers import get_google_photo_uris
from eave.core.orm.account import AccountOrm
from eave.core.orm.account_booking import AccountBookingOrm
from eave.core.orm.activity import ActivityOrm
from eave.core.orm.address_types import Address
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
from eave.core.shared.enums import ActivitySource, RestaurantSource
from eave.core.shared.errors import ValidationError
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
    latitude: float
    longitude: float
    address1: str
    address2: str | None
    city: str
    region: str
    country: str
    postal_code: str
    uri: str
    photo_uri: str | None


async def _get_event_details(
    places_client: PlacesAsyncClient,
    activities_client: EventbriteClient,
    event_source: ActivitySource | RestaurantSource,
    event_id: str,
) -> EventDetails:
    name = address1 = address2 = city = region = postal_code = country = lat = lon = booking_uri = photo_uri = None
    match event_source:
        case ActivitySource.INTERNAL:
            async with database.async_session.begin() as db_session:
                details = await ActivityOrm.get_one(
                    session=db_session,
                    id=UUID(event_id),
                )
            lat, lon = details.coordinates_to_lat_lon()
            name = details.title
            address1 = details.address.address1
            address2 = details.address.address2
            city = details.address.city
            region = details.address.state
            postal_code = details.address.zip
            booking_uri = details.booking_url
        case ActivitySource.GOOGLE_PLACES | RestaurantSource.GOOGLE_PLACES:
            details = await get_place(
                client=places_client,
                id=event_id,
                # field_mask=",".join(["displayName.text", "addressComponents", "location", "websiteUri"]),
            )

            photo_uris = await get_google_photo_uris(
                places_client=places_client,
                photos=details.photos,
            )
            photo_uri = photo_uris[0] if photo_uris else None

            name = details.display_name.text
            booking_uri = details.websiteUri
            country = next(
                (component.shortText for component in details.addressComponents if "country" in component.types),
                None,
            )
            region = next(
                (
                    component.shortText
                    for component in details.addressComponents
                    if "administrative_area_level_1" in component.types
                ),
                None,
            )
            city = next(
                (component.longText for component in details.addressComponents if "locality" in component.types),
                None,
            )
            postal_code = next(
                (component.longText for component in details.addressComponents if "postal_code" in component.types),
                None,
            )
            address1 = next(
                (component.longText for component in details.addressComponents if "street_address" in component.types),
                None,
            ) or " ".join(  # fallback to constructing address from more granular components
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
                        (component.longText for component in details.addressComponents if "route" in component.types),
                        "",
                    ),
                ]
            )
            address2 = next(
                (component.longText for component in details.addressComponents if "subpremise" in component.types),
                None,
            )
            lat = details.location.latitude
            lon = details.location.longitude
        case ActivitySource.EVENTBRITE:
            details = await activities_client.get_event_by_id(
                event_id=event_id,
                query=GetEventQuery(expand=[Expansion.VENUE, Expansion.LOGO]),
            )
            name = details.get("name", {}).get("text")
            booking_uri = details.get("url")
            if venue := details.get("venue"):
                lat = venue.get("latitude")
                lon = venue.get("longitude")
                if address := venue.get("address"):
                    address1 = address.get("address_1")
                    address2 = address.get("address_2")
                    city = address.get("city")
                    region = address.get("region")
                    postal_code = address.get("postal_code")
                    country = address.get("country")
            if logo := details.get("logo"):
                photo_uri = logo.get("original", {}).get("url")

    assert name is not None
    assert lat is not None
    assert lon is not None
    assert address1 is not None
    assert city is not None
    assert region is not None
    assert postal_code is not None
    assert country is not None
    assert booking_uri is not None

    return EventDetails(
        name=name,
        latitude=float(lat),
        longitude=float(lon),
        address1=address1,
        address2=address2,
        city=city,
        region=region,
        postal_code=postal_code,
        country=country,
        uri=booking_uri,
        photo_uri=photo_uri,
    )


async def _create_templates_from_outing(
    db_session: AsyncSession,
    booking_id: UUID,
    outing: OutingOrm,
) -> BookingTemplates:
    places_client = PlacesAsyncClient()
    activities_client = EventbriteClient(api_key=CORE_API_APP_CONFIG.eventbrite_api_key)

    activities = await db_session.scalars(OutingActivityOrm.select().where(OutingActivityOrm.outing_id == outing.id))
    activity_details = []
    for activity in activities:
        src = ActivitySource[activity.activity_source]
        details = await _get_event_details(
            places_client=places_client,
            activities_client=activities_client,
            event_source=src,
            event_id=activity.activity_id,
        )

        activity_details.append(
            await BookingActivityTemplateOrm.build(
                booking_id=booking_id,
                source=src,
                source_id=activity.activity_id,
                activity_name=details.name,
                activity_start_time=activity.activity_start_time,
                headcount=activity.headcount,
                external_booking_link=details.uri,
                address=Address(
                    address1=details.address1,
                    address2=details.address2,
                    city=details.city,
                    state=details.region,
                    zip=details.postal_code,
                    country=details.country,
                ),
                lat=details.latitude,
                lon=details.longitude,
                activity_photo_uri=details.photo_uri,
            ).save(db_session)
        )

    reservations = await db_session.scalars(
        OutingReservationOrm.select().where(OutingReservationOrm.outing_id == outing.id)
    )
    reservation_details = []
    for reservation in reservations:
        src = RestaurantSource[reservation.reservation_source]
        details = await _get_event_details(
            places_client=places_client,
            activities_client=activities_client,
            event_source=src,
            event_id=reservation.reservation_id,
        )

        reservation_details.append(
            await BookingReservationTemplateOrm.build(
                booking_id=booking_id,
                source=src,
                source_id=reservation.reservation_id,
                reservation_name=details.name,
                reservation_start_time=reservation.reservation_start_time,
                headcount=reservation.headcount,
                external_booking_link=details.uri,
                address=Address(
                    address1=details.address1,
                    address2=details.address2,
                    city=details.city,
                    state=details.region,
                    zip=details.postal_code,
                    country=details.country,
                ),
                lat=details.latitude,
                lon=details.longitude,
                reservation_photo_uri=details.photo_uri,
            ).save(db_session)
        )

    return BookingTemplates(
        activities=activity_details,
        reservations=reservation_details,
    )


async def _notify_slack(
    booking_details: BookingTemplates,
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
                    for {reservation.headcount} attendees
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
                    for {activity.headcount} attendees
                    on (ISO time): {activity.activity_start_time.isoformat()}
                    at
                    ```
                    {activity.activity_name}
                    {activity.address}
                    ```
                    """
                        for activity in booking_details.activities
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
                account_id=account_id,
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
