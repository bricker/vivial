from dataclasses import dataclass
from textwrap import dedent


@dataclass
class Address:
    address1: str | None
    address2: str | None
    city: str | None
    state: str | None
    zip: str | None
    country: str | None

    @property
    def formatted(self) -> str:
        out = ""
        if self.address1:
            out += f"{self.address1}"
        if self.address2:
            out += f" {self.address2}"

        if self.city or self.state or self.zip:
            out += "\n"

        if self.city:
            out += f"{self.city}"

        if self.state or self.zip:
            out += ", "

        if self.state:
            out += f"{self.state}"

        if self.zip:
            out += f" {self.zip}"

        return out