import dataclasses

from eave.core.orm.booking import BookingOrm, BookingState
from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.logging import LOGGER
from eave.stdlib.mail import SENDGRID_MAILER
from eave.stdlib.time import pretty_datetime, pretty_time

_WELCOME_EMAIL_TEMPLATE_ID = "d-638ba190b929408aa71a92771a85d817"
_BOOKING_CONFIRMED_EMAIL_TEMPLATE_ID = "d-a277ef6f31364c00b8033ef4b492719f"
_BOOKING_BOOKED_EMAIL_TEMPLATE_ID = "d-28726a7952a641408bd7946e2795e54f"


@dataclasses.dataclass(kw_only=True)
class EventItem:
    time: str
    """time of day event starts. Should be localized to recipient's timezone (e.g. 6:00pm)"""
    name: str


@dataclasses.dataclass(kw_only=True)
class BookingConfirmationData:
    booking_date: str
    """date the outing will occur on (e.g. January 19, 2024)"""
    booking_details_url: str
    activities: list[EventItem]
    restaurants: list[EventItem]


def send_welcome_email(*, to_emails: list[str]) -> None:
    try:
        SENDGRID_MAILER.send_templated_email(
            to_emails=to_emails,
            template_id=_WELCOME_EMAIL_TEMPLATE_ID,
            dynamic_data={},
        )
    except Exception as e:
        if SHARED_CONFIG.is_local:
            raise
        else:
            LOGGER.exception(e)


def send_booking_status_email(*, booking_orm: BookingOrm) -> None:
    data = BookingConfirmationData(
        booking_date=pretty_datetime(booking_orm.start_time_local),
        booking_details_url=f"{SHARED_CONFIG.eave_dashboard_base_url_public}/plans/{booking_orm.id}?utm_source=booking-confirmation-email",
        activities=[
            EventItem(
                name=a.name,
                time=pretty_time(a.start_time_local),
            )
            for a in booking_orm.activities
        ],
        restaurants=[
            EventItem(
                name=r.name,
                time=pretty_time(r.start_time_local),
            )
            for r in booking_orm.reservations
        ],
    )

    match booking_orm.state:
        case BookingState.CONFIRMED:
            template_id = _BOOKING_CONFIRMED_EMAIL_TEMPLATE_ID
        case BookingState.BOOKED:
            template_id = _BOOKING_BOOKED_EMAIL_TEMPLATE_ID
        case _:
            raise ValueError(f"Invalid booking status: {booking_orm.state}")

    try:
        SENDGRID_MAILER.send_templated_email(
            to_emails=[a.email for a in booking_orm.accounts],
            template_id=template_id,
            dynamic_data=dataclasses.asdict(data),
        )
    except Exception as e:
        if SHARED_CONFIG.is_local:
            raise
        else:
            LOGGER.exception(e)
