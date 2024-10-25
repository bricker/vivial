from dataclasses import dataclass

@dataclass
class PaymentOptions:
    acceptsCreditCards: bool
    acceptsDebitCards: bool
    acceptsCashOnly: bool
    acceptsNfc: bool
