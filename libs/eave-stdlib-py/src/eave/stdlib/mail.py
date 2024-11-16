from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Content, Email, Mail, To
import dataclasses
from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.logging import LOGGER


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


class SendgridMailer:
    def __init__(self, api_key: str) -> None:
        self.client = SendGridAPIClient(api_key=api_key)
        self.from_email = Email(email="friends@vivialapp.com", name="Friends @ Vivial")

    def send_html_email(self, to_emails: list[str], subject: str, html_content: str) -> None:
        """
        Send an email with Sendgrid
        https://github.com/sendgrid/sendgrid-python
        """
        message = Mail(
            from_email=self.from_email,
            to_emails=[To(email=email) for email in to_emails],
            subject=subject,
            html_content=Content(mime_type="text/html", content=html_content),
        )
        try:
            self.client.send(message=message)
        except Exception as e:
            LOGGER.exception(e)

    def _send_templated_email(self, template_id: str, to_emails: list[str], dynamic_data: dict[str, str]) -> None:
        """
        Send an email that is defined by a dynamic template in the sendgrid dashboard.
        Template IDs and the expected dynamic data for the target template
        can be located in the dashboard as well.
        https://mc.sendgrid.com/dynamic-templates
        """
        message = Mail(
            from_email=self.from_email,
            to_emails=[To(email=email) for email in to_emails],
        )
        message.template_id = template_id
        message.dynamic_template_data = dynamic_data
        try:
            self.client.send(message=message)
        except Exception as e:
            LOGGER.exception(e)

    def send_welcome_email(self, to_emails: list[str]) -> None:
        self._send_templated_email(
            to_emails=to_emails,
            template_id="d-638ba190b929408aa71a92771a85d817",
            dynamic_data={},
        )

    def send_booking_confirmation_email(self, to_emails: list[str], data: BookingConfirmationData) -> None:
        self._send_templated_email(
            to_emails=to_emails,
            template_id="d-28726a7952a641408bd7946e2795e54f",
            dynamic_data=dataclasses.asdict(data),
        )


MAILER = SendgridMailer(api_key=SHARED_CONFIG.send_grid_api_key)
