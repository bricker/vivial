from typing import TypedDict


class BasicInventoryInfo(TypedDict, total=False):
    """Indicates whether the event has Ticket Classes, Inventory Tiers, Donation Ticket Classes, Ticket Rules, Inventory Add-Ons, and/or Admission Inventory Tiers."""

    has_inventory_tiers: bool
    """True if the event has 1 or more inventory tiers"""

    has_add_ons: bool
    """True if the event has 1 or more inventory tiers where count_against_event_capacity is False"""

    has_ticket_classes: bool
    """True if the event has 1 or more ticket classes"""

    has_donations: bool
    """True if the event has 1 or more ticket classes where `is_donation` is True"""

    has_ticket_rules: bool
    """True if the event has 1 or more ticket rules"""

    has_admission_tiers: bool
    """True if event has 1 or more admission inventory tiers"""

    has_holds: bool
    """True if an event has any type of hold (reserved, GA section, or event capacity)"""

    has_admission_ticket_classes: bool
    """not documented"""

    has_capacity_holds: bool
    """not documented"""

    has_ga_hold_tiers: bool
    """not documented"""

    has_reserved_seating_holds: bool
    """not documented"""

    has_discounts: bool
    """not documented"""
