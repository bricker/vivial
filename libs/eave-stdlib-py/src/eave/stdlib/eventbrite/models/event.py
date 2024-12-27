from enum import StrEnum
from typing import Required, TypedDict

from .category import Category, Subcategory
from .checkout_settings import CheckoutSettings
from .event_sales_status import EventSalesStatus
from .external_ticketing import ExternalTicketing
from .format import Format
from .inventory import BasicInventoryInfo
from .listing_properties import ListingProperties
from .logo import Logo
from .music_properties import MusicProperties
from .organizer import Organizer
from .publish_settings import PublishSettings
from .refund_policy import RefundPolicy
from .shared import DatetimeWithTimezone, MultipartText
from .ticket_availability import TicketAvailability
from .venue import Venue


class EventStatus(StrEnum):
    DRAFT = "draft"
    """A preliminary form of a possible future Event."""

    LIVE = "live"
    """The Event can accept registrations or purchases if ticket classes are available."""

    STARTED = "started"
    """The Event start date has passed."""

    ENDED = "ended"
    """The Event end date has passed."""

    COMPLETED = "completed"
    """The funds for your Event have been paid out."""

    CANCELED = "canceled"
    """The Event has been canceled."""


class EventDescription(TypedDict, total=False):
    """https://www.eventbrite.com/platform/api#/reference/event-description"""

    description: str


class HasDigitalContent(TypedDict, total=False):
    has_digital_content: bool | None
    """whether or not an event has digital content"""

    digital_content_url: str | None
    """The url to the Online Event Page for an event, only accessible if the attendee has purchased a ticket."""

    digital_content_relative_url: str | None
    """not documented"""


class Event(TypedDict, total=False):
    """https://www.eventbrite.com/platform/api#/reference/event"""

    # Expansions: ticket_availability,external_ticketing,basic_inventory_info,event_sales_status,listing_properties,checkout_settings,music_properties,publish_settings,refund_policy,bookmark_info,category,subcategory,format,venue,organizer

    id: str
    """Event ID"""

    resource_uri: str
    """Is an absolute URL to the API endpoint that will return you the canonical representation of the event."""

    name: MultipartText
    """Event name"""

    summary: str
    """Event summary. Short summary describing the event and its purpose. This is a plaintext field and will have any supplied HTML removed from it."""

    description: MultipartText
    """DEPRECATED - Event description (contents of the event page). May be long and have significant formatting."""

    start: DatetimeWithTimezone
    """Start date/time of the event"""

    end: DatetimeWithTimezone
    """End date/time of the event"""

    url: str
    """The URL to the event page for this event on Eventbrite"""

    vanity_url: str | None
    """The vanity URL to the event page for this event on Eventbrite"""

    created: Required[str]
    """When the event was created"""

    changed: Required[str]
    """When the event was last changed"""

    published: str | None
    """When the event was first published"""

    status: EventStatus
    """Status of the event"""

    currency: str
    """The ISO 4217 currency code for this event"""

    online_event: bool
    """If this event doesn't have a venue and is only held online"""

    organization_id: str
    """Organization owning the event"""

    organizer_id: str
    """ID of the event organizer"""

    logo_id: str | None
    """Image ID of the event logo"""

    venue_id: str
    """Event venue ID"""

    format_id: str | None
    """Event format (Expansion: format)"""

    category_id: str | None
    """Event category (Expansion: category)"""

    subcategory_id: str | None
    """Event subcategory (Expansion: subcategory)"""

    listed: bool
    """Is this event publicly searchable on Eventbrite?"""

    shareable: bool
    """Can this event show social sharing buttons?"""

    invite_only: bool
    """Can only people with invites see the event page?"""

    show_remaining: bool
    """Should the event page show the number of tickets left?"""

    capacity: int | None
    """Maximum number of people who can attend."""

    capacity_is_custom: bool | None
    """If True, the value of capacity is a custom-set value; if False, it's a calculated value of the total of all ticket capacities."""

    tx_time_limit: str
    """Maximum duration (in seconds) of a transaction"""

    hide_start_date: bool
    """If true, the event's start date should never be displayed to attendees."""

    hide_end_date: bool
    """If true, the event's end date should never be displayed to attendees."""

    locale: str
    """The event Locale"""

    is_locked: bool
    """nodoc"""

    privacy_setting: str
    """no documentation provided - "unlocked" is the only value I've seen."""

    is_externally_ticketed: bool
    """true, if the Event is externally ticketed"""

    is_series: bool
    """If the event is part of a series"""

    is_series_parent: bool
    """If the event is part of a series and is the series parent"""

    series_id: str | None
    """If the event is part of a series, this is the event id of the series parent. If the event is not part of a series, this field is omitted."""

    is_reserved_seating: bool
    """If the events has been set to have reserved seatings"""

    show_pick_a_seat: bool
    """Enables to show pick a seat option"""

    show_seatmap_thumbnail: bool
    """Enables to show seat map thumbnail"""

    show_colors_in_seatmap_thumbnail: bool
    """For reserved seating event, if venue map thumbnail should have colors on the event page."""

    is_free: bool
    """Allows to set a free event"""

    source: str
    """Source of the event (defaults to API)"""

    version: str | None
    """nodoc"""

    inventory_type: str | None
    """not documented - "limited" is the only value I've seen"""

    facebook_event_id: str | None
    """not documented"""

    ## Expansions

    basic_inventory_info: BasicInventoryInfo | None
    """Indicates whether the event has Ticket Classes, Inventory Tiers, Donation Ticket Classes, Ticket Rules, Inventory Add-Ons, and/or Admission Inventory Tiers."""

    refund_policy: RefundPolicy
    """Event Refund Policy."""

    publish_settings: PublishSettings | None
    """Event publish settings."""

    listing_properties: ListingProperties | None
    """Display/listing details about the event"""

    event_sales_status: EventSalesStatus | None
    """Additional data about the sales status of the event (optional)."""

    checkout_settings: list[CheckoutSettings] | None
    """Additional data about the checkout settings of the Event."""

    external_ticketing: ExternalTicketing | None
    """External ticketing data for the Event."""

    subcategory: Subcategory | None
    """Full details of the event subcategory (requires the subcategory expansion)"""

    music_properties: MusicProperties | None
    """This is an object of properties that detail dimensions of music events."""

    ticket_availability: TicketAvailability | None
    """Additional data about general tickets information (optional)."""

    format: Format | None
    """Full details of the event format (requires the format expansion)"""

    category: Category | None
    """Full details of the event category (requires the category expansion)"""

    venue: Venue | None
    """Full venue details for venue_id (requires the venue expansion)"""

    logo: Logo | None
    """Full image details for event logo (requires the logo expansion)"""

    organizer: Organizer | None
    """Full details of the event organizer (requires the organizer expansion)"""

    has_digital_content: HasDigitalContent | None
    """Whether or not an event Has Digital Content"""
