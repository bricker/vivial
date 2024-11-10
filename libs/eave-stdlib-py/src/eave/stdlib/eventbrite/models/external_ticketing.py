from typing import TypedDict

from .shared import CurrencyCost


class ExternalTicketing(TypedDict, total=True):
    external_url: str
    """The URL clients can follow to purchase tickets."""

    ticketing_provider_name: str
    """The name of the ticketing provider."""

    is_free: bool
    """Whether this is a free event. Mutually exclusive with ticket price range."""

    minimum_ticket_price: CurrencyCost
    """The lowest price at which tickets are being sold."""

    maximum_ticket_price: CurrencyCost
    """The highest price at which tickets are being sold."""

    sales_start: str
    """When sales start."""

    sales_end: str
    """When sales end."""
