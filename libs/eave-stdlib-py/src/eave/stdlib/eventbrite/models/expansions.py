from enum import StrEnum


class Expansion(StrEnum):
    @classmethod
    def all(cls) -> list["Expansion"]:
        return list(cls)

    LOGO = "logo"
    """Event image logo."""

    VENUE = "venue"
    """Event Venue."""

    ORGANIZER = "organizer"
    """Event Organizer."""

    FORMAT = "format"
    """Event Format."""

    CATEGORY = "category"
    """Event Category."""

    SUBCATEGORY = "subcategory"
    """Event Subcategory."""

    BOOKMARK_INFO = "bookmark_info"
    """
    Indicates whether a user has saved the Event as a bookmark.
    Returns false if there are no bookmarks.
    If there are bookmarks, returns a a dictionary specifying the number of end-users who have bookmarked the Event as a count object like {count:3}.
    """

    REFUND_POLICY = "refund_policy"
    """Event Refund Policy."""

    TICKET_AVAILABILITY = "ticket_availability"
    """Overview of availability of all Ticket Classes"""

    EXTERNAL_TICKETING = "external_ticketing"
    """External ticketing data for the Event."""

    MUSIC_PROPERTIES = "music_properties"
    """Event Music Properties"""

    PUBLISH_SETTINGS = "publish_settings"
    """Event publish settings."""

    BASIC_INVENTORY_INFO = "basic_inventory_info"
    """Indicates whether the event has Ticket Classes, Inventory Tiers, Donation Ticket Classes, Ticket Rules, Inventory Add-Ons, and/or Admission Inventory Tiers."""

    EVENT_SALES_STATUS = "event_sales_status"
    """Event's sales status details"""

    CHECKOUT_SETTINGS = "checkout_settings"
    """Event checkout and payment settings."""

    LISTING_PROPERTIES = "listing_properties"
    """Display/listing details about the event"""

    HAS_DIGITAL_CONTENT = "has_digital_content"
    """Whether or not an event Has Digital Content"""
