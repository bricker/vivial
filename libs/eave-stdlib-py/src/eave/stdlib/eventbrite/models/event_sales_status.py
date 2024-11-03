from enum import StrEnum
from typing import TypedDict

from eave.stdlib.eventbrite.models.shared import DatetimeWithTimezone


class EventSalesStatusSalesStatus(StrEnum):
    text = "text"
    """not documented - perhaps a custom status"""

    on_sale = "on_sale"
    """The event has tickets currently available for sale."""

    not_yet_on_sale = "not_yet_on_sale"
    """All available tickets for the event have their start sales in the future."""

    sales_ended = "sales_ended"
    """All available tickets for the event have their sales ended."""

    sold_out = "sold_out"
    """An Event is sold out if we have no tickets to sell and also we don't have hidden tickets availables."""

    unavailable = "unavailable"
    """This status is when we are not under 'sold out' state but have no available tickets to sell. Could it be because event has a soft sell-out at current point of time due to pending order."""


class EventSalesStatusMessageType(StrEnum):
    default = "default"
    """The message returned is the default message for this event status."""

    canonical = "canonical"
    """The message returned is the default message for another (canonical) event status."""

    custom = "custom"
    """The message returned is a custom message for this event status."""


class EventSalesStatusMessageCode(StrEnum):
    tickets_not_yet_on_sale = "tickets_not_yet_on_sale"
    """Custom text for event sales status with tickets not yet on sale."""

    tickets_with_sales_ended = "tickets_with_sales_ended"
    """Custom text for event sales status when their tickets have sales ended."""

    tickets_sold_out = "tickets_sold_out"
    """Custom text for event sales status with tickets are sold out."""

    tickets_unavailable = "tickets_unavailable"
    """Custom text for event sales status with tickets are unavailable."""

    tickets_at_the_door = "tickets_at_the_door"
    """Custom text for event sales status with tickets are at the door only."""

    event_cancelled = "event_cancelled"
    """Custom text when an event has their sales cancelled."""

    event_postponed = "event_postponed"
    """Custom text when an event has their sales postponed."""


class EventSalesStatus(TypedDict, total=False):
    """Additional data about the sales status of the event."""

    sales_status: EventSalesStatusSalesStatus
    """Current sales status of the event."""

    start_sales_date: DatetimeWithTimezone | None
    """The earliest start time when a visible ticket is or will be available"""

    message: str
    """Custom message associated with the current event sales status."""

    message_type: EventSalesStatusMessageType
    """nodoc"""

    message_code: EventSalesStatusMessageCode
    """The message returned is overridden by the following event status message."""

    currency: str | None
    """not documented"""
