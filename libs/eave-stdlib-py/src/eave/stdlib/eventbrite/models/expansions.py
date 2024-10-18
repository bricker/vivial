from enum import StrEnum


class Expansion(StrEnum):
    logo = "logo"
    """Event image logo."""

    venue = "venue"
    """Event Venue."""

    organizer = "organizer"
    """Event Organizer."""

    format_ = "format"
    """Event Format."""

    category = "category"
    """Event Category."""

    subcategory = "subcategory"
    """Event Subcategory."""

    bookmark_info = "bookmark_info"
    """
    Indicates whether a user has saved the Event as a bookmark.
    Returns false if there are no bookmarks.
    If there are bookmarks, returns a a dictionary specifying the number of end-users who have bookmarked the Event as a count object like {count:3}.
    """

    refund_policy = "refund_policy"
    """Event Refund Policy."""

    ticket_availability = "ticket_availability"
    """Overview of availability of all Ticket Classes"""

    external_ticketing = "external_ticketing"
    """External ticketing data for the Event."""

    music_properties = "music_properties"
    """Event Music Properties"""

    publish_settings = "publish_settings"
    """Event publish settings."""

    basic_inventory_info = "basic_inventory_info"
    """Indicates whether the event has Ticket Classes, Inventory Tiers, Donation Ticket Classes, Ticket Rules, Inventory Add-Ons, and/or Admission Inventory Tiers."""

    event_sales_status = "event_sales_status"
    """Event's sales status details"""

    checkout_settings = "checkout_settings"
    """Event checkout and payment settings."""

    listing_properties = "listing_properties"
    """Display/listing details about the event"""

    has_digital_content = "has_digital_content"
    """Whether or not an event Has Digital Content"""
