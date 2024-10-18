from typing import TypedDict


class RefundPolicy(TypedDict, total=False):
    """Event Refund Policy."""

    refund_policy: str | None
    """not documented - an enum with "custom" the only value I've seen"""

    refund_retention_policy: object | None  # unknown
    """not documented"""

    is_attendee_automated_refund_allowed: bool | None
    """not documented"""

    default_refund_retention_policy_strategy: object | None  # unknown
    """not documented"""

    refund_methods: list[str] | None
    """not documented - only value I've seen is 'original_payment'"""

    credit_expiration_period: object | None  # unknown
    """not documented"""

    is_refund_request_allowed: bool | None
    """not documented"""

    validity_days: int | None
    """not documented"""

    refund_policy_description: str | None
    """not documented"""
