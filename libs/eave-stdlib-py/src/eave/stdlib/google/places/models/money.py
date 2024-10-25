from dataclasses import dataclass

@dataclass
class Money:
    currencyCode: str
    units: str
    nanos: int
