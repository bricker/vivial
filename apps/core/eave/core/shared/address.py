from dataclasses import dataclass
from textwrap import dedent


@dataclass
class Address:
    address1: str
    address2: str | None
    city: str
    state: str
    zip: str
    country: str

    def formatted(self) -> str:
        return dedent(f"""
            {self.address1} {self.address2}
            {self.city}, {self.state} {self.zip}
            """).strip()
