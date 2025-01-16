from typing import Any, Mapping
import sendgrid
from sendgrid.helpers.mail import Content, Email, Mail, To

from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.exceptions import suppress_in_production
from eave.stdlib.logging import LOGGER


class SendgridMailer:
    client: sendgrid.SendGridAPIClient
    from_email: Email

    def __init__(self) -> None:
        self.client = sendgrid.SendGridAPIClient(api_key=SHARED_CONFIG.send_grid_api_key)
        self.from_email = Email(email="friends@vivialapp.com", name="Friends @ Vivial")

    def send_html_email(self, to_emails: list[str], subject: str, html_content: str, *, ctx: Mapping[str, Any] | None = None) -> None:
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
        if SHARED_CONFIG.mailer_enabled:
            with suppress_in_production(Exception, ctx=ctx):
                self.client.send(message=message)
        else:
            LOGGER.warning("Mailer disabled - not sending any emails", ctx)

    def send_templated_email(self, template_id: str, to_emails: list[str], dynamic_data: dict[str, str], *, ctx: Mapping[str, Any] | None = None) -> None:
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
        if SHARED_CONFIG.mailer_enabled:
            with suppress_in_production(Exception, ctx=ctx):
                self.client.send(message=message)
        else:
            LOGGER.warning("Mailer disabled - not sending any emails", ctx)


SENDGRID_MAILER = SendgridMailer()
