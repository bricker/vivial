import dataclasses

from eave.stdlib.mail import SendgridMailer


@dataclasses.dataclass(kw_only=True)
class EventItem:
    time: str
    """time of day event starts. Should be localized to recipient's timezone (e.g. 6:00pm)"""
    name: str


@dataclasses.dataclass(kw_only=True)
class BookingConfirmationData:
    booking_date: str
    """date the outing will occur on (e.g. January 19, 2024)"""
    activities: list[EventItem]
    restaurants: list[EventItem]


def send_welcome_email(to_emails: list[str]) -> None:
    mailer = SendgridMailer()
    mailer.send_templated_email(
        to_emails=to_emails,
        template_id="d-638ba190b929408aa71a92771a85d817",
        dynamic_data={},
    )


def send_booking_confirmation_email(to_emails: list[str], data: BookingConfirmationData) -> None:
    mailer = SendgridMailer()
    mailer.send_templated_email(
        to_emails=to_emails,
        template_id="d-28726a7952a641408bd7946e2795e54f",
        dynamic_data=dataclasses.asdict(data),
    )
