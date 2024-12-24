import dataclasses

from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.logging import LOGGER
from eave.stdlib.mail import SENDGRID_MAILER


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


def send_welcome_email(to_email: str) -> None:
    try:
        SENDGRID_MAILER.send_templated_email(
            to_emails=[to_email],
            template_id="d-638ba190b929408aa71a92771a85d817",
            dynamic_data={},
        )
    except Exception as e:
        if SHARED_CONFIG.is_local:
            raise
        else:
            LOGGER.exception(e)


def send_booking_confirmation_email(*, to_email: str, data: BookingConfirmationData) -> None:
    try:
        SENDGRID_MAILER.send_templated_email(
            to_emails=[to_email],
            template_id="d-28726a7952a641408bd7946e2795e54f",
            dynamic_data=dataclasses.asdict(data),
        )
    except Exception as e:
        if SHARED_CONFIG.is_local:
            raise
        else:
            LOGGER.exception(e)
