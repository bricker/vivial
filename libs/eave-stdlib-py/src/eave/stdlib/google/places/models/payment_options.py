from typing import TypedDict


class PaymentOptions(TypedDict, total=False):
    """https://developers.google.com/maps/documentation/places/web-service/reference/rest/v1/places#PaymentOptions"""

    acceptsCreditCards: bool
    acceptsDebitCards: bool
    acceptsCashOnly: bool
    acceptsNfc: bool
