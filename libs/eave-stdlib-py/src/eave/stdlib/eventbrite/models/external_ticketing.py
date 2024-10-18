from typing import TypedDict

from .shared import Price


class ExternalTicketing(TypedDict, total=False):
    external_url: str | None
    """The URL clients can follow to purchase tickets."""

    ticketing_provider_name: str | None
    """The name of the ticketing provider."""

    is_free: bool | None
    """Whether this is a free event. Mutually exclusive with ticket price range."""

    minimum_ticket_price: Price | None
    """The lowest price at which tickets are being sold."""

    maximum_ticket_price: Price | None
    """The highest price at which tickets are being sold."""

    sales_start: str | None
    """When sales start."""

    sales_end: str | None
    """When sales end."""
