import dataclasses

from eave.core.orm.booking import BookingOrm
from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.logging import LOGGER
from eave.stdlib.mail import SENDGRID_MAILER
from eave.stdlib.time import pretty_datetime, pretty_time


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
            template_id="d-638ba190b929408aa71a92771a85d817",
            dynamic_data={},
        )
    except Exception as e:
        if SHARED_CONFIG.is_local:
            raise
        else:
            LOGGER.exception(e)


def send_booking_confirmation_email(*, booking_orm: BookingOrm) -> None:
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

    try:
        SENDGRID_MAILER.send_templated_email(
            to_emails=[a.email for a in booking_orm.accounts],
            template_id="d-28726a7952a641408bd7946e2795e54f",
            dynamic_data=dataclasses.asdict(data),
        )
    except Exception as e:
        if SHARED_CONFIG.is_local:
            raise
        else:
            LOGGER.exception(e)
