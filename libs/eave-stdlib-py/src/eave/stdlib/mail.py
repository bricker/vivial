from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Content, Email, Mail, To

from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.logging import LOGGER


class SendgridMailer:
    def __init__(self, api_key: str) -> None:
        self.client = SendGridAPIClient(api_key=api_key)

    def send_email(self, to_emails: list[str], subject: str, html_content: str) -> None:
        """
        Send an email with Sendgrid
        https://github.com/sendgrid/sendgrid-python
        """
        message = Mail(
            from_email=Email(email="friends@vivialapp.com", name="Friends @ Vivial"),
            to_emails=[To(email=email) for email in to_emails],
            subject=subject,
            html_content=Content(mime_type="text/html", content=html_content),
        )
        try:
            self.client.send(message=message)
        except Exception as e:
            LOGGER.exception(e)


MAILER = SendgridMailer(api_key=SHARED_CONFIG.send_grid_api_key)
