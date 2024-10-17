from typing import TypedDict

from eave.stdlib.eventbrite.models.shared import DatetimeWithTimezone, Price


class TicketAvailability(TypedDict, total=False):
    """Additional data about general tickets information"""

    has_available_tickets: bool | None
    """Whether this event has tickets available to purchase"""

    minimum_ticket_price: Price | None
    """A dictionary with some data of the available ticket with the minimum"""

    maximum_ticket_price: Price | None
    """A dictionary with some data of the available ticket with the maximum"""

    is_sold_out: bool | None
    """Whether there is at least one ticket with availability"""

    start_sales_date: DatetimeWithTimezone | None
    """The earliest start time when a visible ticket is or will be available"""

    waitlist_available: bool | None
    """nodoc"""
