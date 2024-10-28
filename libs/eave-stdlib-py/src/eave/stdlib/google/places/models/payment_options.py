from typing import TypedDict


class PaymentOptions(TypedDict, total=False):
    acceptsCreditCards: bool
    acceptsDebitCards: bool
    acceptsCashOnly: bool
    acceptsNfc: bool
