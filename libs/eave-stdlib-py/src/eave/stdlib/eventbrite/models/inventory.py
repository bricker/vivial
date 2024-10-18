from typing import TypedDict


class BasicInventoryInfo(TypedDict, total=False):
    """Indicates whether the event has Ticket Classes, Inventory Tiers, Donation Ticket Classes, Ticket Rules, Inventory Add-Ons, and/or Admission Inventory Tiers."""

    has_ticket_classes: bool | None
    """not documented"""

    has_inventory_tiers: bool | None
    """not documented"""

    has_ticket_rules: bool | None
    """not documented"""

    has_add_ons: bool | None
    """not documented"""

    has_donations: bool | None
    """not documented"""

    has_admission_tiers: bool | None
    """not documented"""

    has_admission_ticket_classes: bool | None
    """not documented"""

    has_capacity_holds: bool | None
    """not documented"""

    has_ga_hold_tiers: bool | None
    """not documented"""

    has_reserved_seating_holds: bool | None
    """not documented"""

    has_holds: bool | None
    """not documented"""

    has_discounts: bool | None
    """not documented"""
