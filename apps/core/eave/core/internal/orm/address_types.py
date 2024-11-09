from typing import Any, Literal, NamedTuple

from sqlalchemy import Dialect
from sqlalchemy.sql.type_api import _ResultProcessorType
from sqlalchemy.types import UserDefinedType


class PostgisStdaddr(NamedTuple):
    """https://www.postgis.net/docs/manual-2.5/stdaddr.html"""

    # WARNING: The order of these fields must not change.

    building: str | None
    """is text (token number 0): Refers to building number or name. Unparsed building identifiers and types. Generally blank for most addresses."""

    house_num: str | None
    """is a text (token number 1): This is the street number on a street. Example 75 in 75 State Street."""

    predir: str | None
    """is text (token number 2): STREET NAME PRE-DIRECTIONAL such as North, South, East, West etc."""

    qual: str | None
    """is text (token number 3): STREET NAME PRE-MODIFIER Example OLD in 3715 OLD HIGHWAY 99."""

    pretype: str | None
    """is text (token number 4): STREET PREFIX TYPE"""

    name: str | None
    """is text (token number 5): STREET NAME"""

    suftype: str | None
    """is text (token number 6): STREET POST TYPE e.g. St, Ave, Cir. A street type following the root street name. Example STREET in 75 State Street."""

    sufdir: str | None
    """is text (token number 7): STREET POST-DIRECTIONAL A directional modifier that follows the street name.. Example WEST in 3715 TENTH AVENUE WEST."""

    ruralroute: str | None
    """is text (token number 8): RURAL ROUTE . Example 7 in RR 7."""

    extra: str | None
    """is text: Extra information like Floor number."""

    city: str | None
    """is text (token number 10): Example Boston."""

    state: str | None
    """is text (token number 11): Example MASSACHUSETTS"""

    country: str | None
    """is text (token number 12): Example USA"""

    postcode: str | None
    """is text POSTAL CODE (ZIP CODE) (token number 13): Example 02109"""

    box: str | None
    """is text POSTAL BOX NUMBER (token number 14 and 15): Example 02109"""

    unit: str | None
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
