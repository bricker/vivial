from enum import StrEnum
from typing import TypedDict

from eave.stdlib.eventbrite.models.shared import DatetimeWithTimezone


class EventSalesStatusSalesStatus(StrEnum):
    TEXT = "text"
    """not documented - perhaps a custom status"""

    ON_SALE = "on_sale"
    """The event has tickets currently available for sale."""

    NOT_YET_ON_SALE = "not_yet_on_sale"
    """All available tickets for the event have their start sales in the future."""

    SALES_ENDED = "sales_ended"
    """All available tickets for the event have their sales ended."""

    SOLD_OUT = "sold_out"
    """An Event is sold out if we have no tickets to sell and also we don't have hidden tickets availables."""

    UNAVAILABLE = "unavailable"
    """This status is when we are not under 'sold out' state but have no available tickets to sell. Could it be because event has a soft sell-out at current point of time due to pending order."""


class EventSalesStatusMessageType(StrEnum):
    DEFAULT = "default"
    """The message returned is the default message for this event status."""

    CANONICAL = "canonical"
    """The message returned is the default message for another (canonical) event status."""

    CUSTOM = "custom"
    """The message returned is a custom message for this event status."""


class EventSalesStatusMessageCode(StrEnum):
    TICKETS_NOT_YET_ON_SALE = "tickets_not_yet_on_sale"
    """Custom text for event sales status with tickets not yet on sale."""

    TICKETS_WITH_SALES_ENDED = "tickets_with_sales_ended"
    """Custom text for event sales status when their tickets have sales ended."""

    TICKETS_SOLD_OUT = "tickets_sold_out"
    """Custom text for event sales status with tickets are sold out."""

    TICKETS_UNAVAILABLE = "tickets_unavailable"
    """Custom text for event sales status with tickets are unavailable."""

    TICKETS_AT_THE_DOOR = "tickets_at_the_door"
    """Custom text for event sales status with tickets are at the door only."""

    EVENT_CANCELLED = "event_cancelled"
    """Custom text when an event has their sales cancelled."""

    EVENT_POSTPONED = "event_postponed"
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
