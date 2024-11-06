from enum import StrEnum
from typing import Required, TypedDict


class CheckoutMethod(StrEnum):
    """The checkout method to use for completing consumer payment for tickets or other goods."""

    PAYPAL = "paypal"

    EVENTBRITE = "eventbrite"

    AUTHNET = "authnet"

    OFFLINE = "offline"


class PaymentMethod(StrEnum):
    CASH = "CASH"

    CHECK = "CHECK"

    INVOICE = "INVOICE"


class OfflineSettings(TypedDict, total=False):
    """A container for representing additional offline payment method checkout settings."""

    payment_method: PaymentMethod | None
    """nodoc"""

    instructions: str | None
    """nodoc"""


class CheckoutSettings(TypedDict, total=False):
    """Additional data about the checkout settings of the Event."""

    id: Required[str]
    """not documented"""

    resource_uri: Required[str]
    """not documented"""

    created: str | None
    """When the checkout settings object was created"""

    changed: str | None
    """When the checkout settings object was last changed"""

    offline_settings: list[OfflineSettings] | None
    """A container for representing additional offline payment method checkout settings."""

    country_code: str | None
    """The ISO 3166 alpha-2 code of the country within which these checkout settings can apply."""

    currency_code: str | None
    """The ISO 4217 3-character code of the currency for which these checkout settings can apply."""

    checkout_method: CheckoutMethod | None
    """The checkout method to use for completing consumer payment for tickets or other goods."""

    user_instrument_vault_id: str | None
    """The merchant account user instrument ID for the checkout method. Only specify this value for PayPal and Authorize.net checkout settings."""
