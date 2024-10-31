from uuid import UUID

from eave.stdlib.eventbrite.client import EventbriteClient, GetEventQuery
from eave.stdlib.google.places.client import GooglePlacesClient
from eave.stdlib.util import extract_nested_field
import strawberry
from attr import dataclass
from sqlalchemy.ext.asyncio import AsyncSession

import eave.stdlib.slack
from eave.core.graphql.types.booking import (
    Booking,
    CreateBookingError,
    CreateBookingErrorCode,
    CreateBookingResult,
    CreateBookingSuccess,
)
from eave.core.internal import database
from eave.core.internal.config import CORE_API_APP_CONFIG
from eave.core.internal.orm.account import AccountOrm
from eave.core.internal.orm.account_booking import AccountBookingOrm
from eave.core.internal.orm.booking import BookingOrm
from eave.core.internal.orm.booking_activities_template import BookingActivityTemplateOrm
from eave.core.internal.orm.booking_reservations_template import BookingReservationTemplateOrm
from eave.core.internal.orm.outing import OutingOrm
from eave.core.internal.orm.outing_activity import OutingActivityOrm
from eave.core.internal.orm.outing_reservation import OutingReservationOrm
from eave.core.internal.orm.reserver_details import ReserverDetailsOrm
from eave.core.internal.orm.survey import SurveyOrm
from eave.core.internal.orm.util import validate_time_within_bounds_or_exception
from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.exceptions import InvalidDataError, StartTimeTooLateError, StartTimeTooSoonError
from eave.stdlib.logging import LOGGER

from eave.core.outing.models.sources import EventSource


@dataclass
class BookingDetails:
    activities: list[BookingActivityTemplateOrm]
    reservations: list[BookingReservationTemplateOrm]


@dataclass
class EventDetails:
    name: str
    latitude: float
    longitude: float
    address1: str
    address2: str
    city: str
    region: str
    country: str
    postal_code: str
    uri: str


async def _get_event_details(
    places_client: GooglePlacesClient, activities_client: EventbriteClient, event_source: EventSource, remote_id: str
) -> EventDetails:
    name = address1 = address2 = city = region = postal_code = country = lat = lon = booking_uri = None
    match event_source:
        case EventSource.INTERNAL:
            # TODO: fetch from internal db
            details = None
        case EventSource.GOOGLE_PLACES:
            details = await places_client.get_place_details(
                id=remote_id,
                field_mask=["displayName.text", "addressComponents", "location", "websiteUri"],
            )

            name = extract_nested_field(details, "displayName", "text")
            booking_uri = details.get("websiteUri")
            country = next(
                (
                    component.get("shortText")
                    for component in details.get("addressComponents") or []
                    if "country" in component.get("types", [])
                ),
                None,
            )
            region = next(
                (
                    component.get("shortText")
                    for component in details.get("addressComponents") or []
                    if "administrative_area_level_1" in component.get("types", [])
                ),
                None,
            )
            city = next(
                (
                    component.get("longText")
                    for component in details.get("addressComponents") or []
                    if "locality" in component.get("types", [])
                ),
                None,
            )
            postal_code = next(
                (
                    component.get("longText")
                    for component in details.get("addressComponents") or []
                    if "postal_code" in component.get("types", [])
                ),
                None,
            )
            address1 = next(
                (
                    component.get("longText")
                    for component in details.get("addressComponents") or []
                    if "street_address" in component.get("types", [])
                ),
                None,
            ) or " ".join(  # fallback to constructing address from more granular components
                [
                    next(
                        (
                            component.get("longText", "")
                            for component in details.get("addressComponents") or []
                            if "street_number" in component.get("types", [])
                        ),
                        "",
                    ),
                    next(
                        (
                            component.get("longText", "")
                            for component in details.get("addressComponents") or []
                            if "route" in component.get("types", [])
                        ),
                        "",
                    ),
                ]
            )
            address2 = next(
                (
                    component.get("longText")
                    for component in details.get("addressComponents") or []
                    if "subpremise" in component.get("types", [])
                ),
                None,
            )
            lat = extract_nested_field(details, "location", "latitude")
            lon = extract_nested_field(details, "location", "longitude")
        case EventSource.EVENTBRITE:
            details = await activities_client.get_event_by_id(
                event_id=remote_id,
                query=GetEventQuery(expand="venue"),
            )
            name = extract_nested_field(details, "name", "text")
            booking_uri = details.get("url")
            address1 = extract_nested_field(details, "venue", "address", "address_1")
            address2 = extract_nested_field(details, "venue", "address", "address_2")
            city = extract_nested_field(details, "venue", "address", "city")
            region = extract_nested_field(details, "venue", "address", "region")
            postal_code = extract_nested_field(details, "venue", "address", "postal_code")
            country = extract_nested_field(details, "venue", "address", "country")
            lat = extract_nested_field(details, "venue", "latitude")
            lon = extract_nested_field(details, "venue", "longitude")

    assert name is not None
    assert lat is not None
    assert lon is not None
    assert address1 is not None
    assert address2 is not None  # TODO: maybe ok if addr2 is nullable? not everywhere has appartment number or somthing
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
    )


async def _create_templates_from_outing(
    db_session: AsyncSession,
    booking_id: UUID,
    outing: OutingOrm,
) -> BookingDetails:
    places_client = GooglePlacesClient(api_key=CORE_API_APP_CONFIG.google_places_api_key)
    activities_client = EventbriteClient(api_key=CORE_API_APP_CONFIG.eventbrite_api_key)

    activities = await OutingActivityOrm.query(
        session=db_session,
        params=OutingActivityOrm.QueryParams(outing_id=outing.id),
    )
    activity_details = []
    for activity in activities:
        src = EventSource.from_str(activity.activity_source)
        assert src is not None
        details = await _get_event_details(
            places_client=places_client,
            activities_client=activities_client,
            event_source=src,
            remote_id=activity.activity_id,
        )

        activity_details.append(
            await BookingActivityTemplateOrm.create(
                session=db_session,
                booking_id=booking_id,
                activity_name=details.name,
                activity_start_time=activity.activity_start_time,
                num_attendees=activity.num_attendees,
                external_booking_link=details.uri,
                activity_location_address1=details.address1,
                activity_location_address2=details.address2,
                activity_location_city=details.city,
                activity_location_region=details.region,
                activity_location_country=details.country,
                activity_location_latitude=details.latitude,
                activity_location_longitude=details.longitude,
            )
        )

    reservations = await OutingReservationOrm.query(
        session=db_session,
        params=OutingReservationOrm.QueryParams(outing_id=outing.id),
    )
    reservation_details = []
    for reservation in reservations:
        src = EventSource.from_str(reservation.reservation_source)
        assert src is not None
        details = await _get_event_details(
            places_client=places_client,
            activities_client=activities_client,
            event_source=src,
            remote_id=reservation.reservation_id,
        )

        reservation_details.append(
            await BookingReservationTemplateOrm.create(
                session=db_session,
                booking_id=booking_id,
                reservation_name=details.name,
                reservation_start_time=reservation.reservation_start_time,
                num_attendees=reservation.num_attendees,
                external_booking_link=details.uri,
                reservation_location_address1=details.address1,
                reservation_location_address2=details.address2,
                reservation_location_city=details.city,
                reservation_location_region=details.region,
                reservation_location_country=details.country,
                reservation_location_latitude=details.latitude,
                reservation_location_longitude=details.longitude,
            )
        )

    return BookingDetails(
        activities=activity_details,
        reservations=reservation_details,
    )


async def _notify_slack(
    booking_details: BookingDetails,
    account_id: UUID,
    reserver_details_id: UUID,
) -> None:
    async with database.async_session.begin() as db_session:
        account = await AccountOrm.one_or_exception(
            session=db_session,
            params=AccountOrm.QueryParams(id=account_id),
        )
        reserver = await ReserverDetailsOrm.one_or_exception(
            session=db_session,
            params=ReserverDetailsOrm.QueryParams(id=reserver_details_id),
        )
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
                text=(
                    f""""
Account ID: `{account.id}`
Account email: `{account.email}`

Reserver first name: `{reserver.first_name}`
Reserver last name: `{reserver.last_name}`
Reserver phone number: `{reserver.phone_number}`

{"\n".join([
f"""*Reservation:*
for {reservation.num_attendees} attendees
on (ISO time): {reservation.reservation_start_time.isoformat()}
at
```
{reservation.reservation_name}
{reservation.reservation_location_address1}
{reservation.reservation_location_address2}
{reservation.reservation_location_city}, {reservation.reservation_location_region}
{reservation.reservation_location_country}
```
"""
    for reservation in booking_details.reservations
])}

{"\n".join([
f"""*Activity:*
for {activity.num_attendees} attendees
on (ISO time): {activity.activity_start_time.isoformat()}
at
```
{activity.activity_name}
{activity.activity_location_address1}
{activity.activity_location_address2}
{activity.activity_location_city}, {activity.activity_location_region}
{activity.activity_location_country}
```
"""
    for activity in booking_details.activities
])}
"""
                ),
            )
    except Exception as e:
        LOGGER.exception(e)


async def create_booking_mutation(
    *,
    info: strawberry.Info,
    account_id: UUID,  # TODO: need this here? or get auth from elsewhere?
    outing_id: UUID,
    reserver_details_id: UUID,
) -> CreateBookingResult:
    try:
        async with database.async_session.begin() as db_session:
            # TODO: should we 1 or none and return client friendly error if 404? instead of 500 throw
            outing = await OutingOrm.one_or_exception(
                session=db_session,
                params=OutingOrm.QueryParams(id=outing_id),
            )
            survey = await SurveyOrm.one_or_exception(
                session=db_session, params=SurveyOrm.QueryParams(id=outing.survey_id)
            )
            # validate outing time still valid to book
            try:
                validate_time_within_bounds_or_exception(survey.start_time)
            except StartTimeTooSoonError:
                raise InvalidDataError(code=CreateBookingErrorCode.START_TIME_TOO_SOON)
            except StartTimeTooLateError:
                raise InvalidDataError(code=CreateBookingErrorCode.START_TIME_TOO_LATE)

            booking = await BookingOrm.create(
                session=db_session,
                reserver_details_id=reserver_details_id,
            )

            await AccountBookingOrm.create(
                session=db_session,
                account_id=account_id,
                booking_id=booking.id,
            )
            booking_details = await _create_templates_from_outing(
                db_session=db_session,
                booking_id=booking.id,
                outing=outing,
            )
    except InvalidDataError as e:
        LOGGER.exception(e)
        return CreateBookingError(error_code=CreateBookingErrorCode(e.code))

    await _notify_slack(booking_details, account_id, reserver_details_id)

    return CreateBookingSuccess(
        booking=Booking(
            id=booking.id,
            reserver_details_id=booking.reserver_details_id,
        )
    )
