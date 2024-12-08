from dataclasses import dataclass


@dataclass
class Address:
    address1: str
    address2: str | None
    city: str
    state: str
    zip: str
    country: str