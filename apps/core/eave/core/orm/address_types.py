from dataclasses import dataclass
from typing import Any, Literal, NamedTuple

from sqlalchemy import Dialect
from sqlalchemy.sql.type_api import _ResultProcessorType, _BindProcessorType
from sqlalchemy.types import UserDefinedType


class PostgisStdaddr(NamedTuple):
    """https://www.postgis.net/docs/manual-2.5/stdaddr.html"""

    # WARNING: The order of these fields must not change.

    building: str | None = None
    """is text (token number 0): Refers to building number or name. Unparsed building identifiers and types. Generally blank for most addresses."""

    house_num: str | None = None
    """is a text (token number 1): This is the street number on a street. Example 75 in 75 State Street."""

    predir: str | None = None
    """is text (token number 2): STREET NAME PRE-DIRECTIONAL such as North, South, East, West etc."""

    qual: str | None = None
    """is text (token number 3): STREET NAME PRE-MODIFIER Example OLD in 3715 OLD HIGHWAY 99."""

    pretype: str | None = None
    """is text (token number 4): STREET PREFIX TYPE"""

    name: str | None = None
    """is text (token number 5): STREET NAME"""

    suftype: str | None = None
    """is text (token number 6): STREET POST TYPE e.g. St, Ave, Cir. A street type following the root street name. Example STREET in 75 State Street."""

    sufdir: str | None = None
    """is text (token number 7): STREET POST-DIRECTIONAL A directional modifier that follows the street name.. Example WEST in 3715 TENTH AVENUE WEST."""

    ruralroute: str | None = None
    """is text (token number 8): RURAL ROUTE . Example 7 in RR 7."""

    extra: str | None = None
    """is text: Extra information like Floor number."""

    city: str | None = None
    """is text (token number 10): Example Boston."""

    state: str | None = None
    """is text (token number 11): Example MASSACHUSETTS"""

    country: str | None = None
    """is text (token number 12): Example USA"""

    postcode: str | None = None
    """is text POSTAL CODE (ZIP CODE) (token number 13): Example 02109"""

    box: str | None = None
    """is text POSTAL BOX NUMBER (token number 14 and 15): Example 02109"""

    unit: str | None = None
    """is text Apartment number or Suite Number (token number 17): Example 3B in APT 3B."""

class PostgisStdaddrColumnType(UserDefinedType):
    cache_ok = True

    def get_col_spec(self) -> Literal["stdaddr"]:
        return "stdaddr"

    def result_processor(self, dialect: Dialect, coltype: object) -> _ResultProcessorType[PostgisStdaddr] | None:
        def process(value: Any) -> PostgisStdaddr | None:
            # For asyncpg, `value` is a asyncpg.Record. Basically it's a tuple.
            return PostgisStdaddr(*value)

        return process

class ParsedAddress(NamedTuple):
    """https://postgis.net/docs/manual-3.0/parse_address.html"""

    # WARNING: The order of these fields must not change.

    num: str | None
    street: str | None
    street2: str | None
    address1: str | None
    city: str | None
    state: str | None
    zip: str | None
    zipplus: str | None
    country: str | None

class PostgisParsedAddressColumnType(UserDefinedType):
    cache_ok = True

    def get_col_spec(self) -> Literal["JSON"]:
        return "JSON"

    def bind_processor(
        self, dialect: Dialect
    ) -> _BindProcessorType[ParsedAddress] | None:
        def process(value: ParsedAddress | None) -> ParsedAddress:
            return value

        return process

    def result_processor(self, dialect: Dialect, coltype: object) -> _ResultProcessorType[ParsedAddress] | None:
        def process(value: Any) -> ParsedAddress | None:
            # For asyncpg, `value` is a asyncpg.Record. Basically it's a tuple.
            return ParsedAddress(**value)

        return process

@dataclass
class Address:
    address1: str
    address2: str | None
    city: str
    state: str
    zip: str
    country: str

class AddressColumnType(UserDefinedType):
    cache_ok = True

    def get_col_spec(self) -> Literal["JSON"]:
        return "JSON"

    def bind_processor(
        self, dialect: Dialect
    ) -> _BindProcessorType[Address] | None:
        def process(value: Address | None) -> dict[str, Any]:
            return value.__dict__

        return process

    def result_processor(self, dialect: Dialect, coltype: object) -> _ResultProcessorType[Address] | None:
        def process(value: Any) -> Address | None:
            # For asyncpg, `value` is a asyncpg.Record. Basically it's a tuple.
            return Address(**value)

        return process
