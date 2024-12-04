import dataclasses
import json
from dataclasses import dataclass
from typing import Any, Literal

from sqlalchemy import Dialect
from sqlalchemy.sql.type_api import _BindProcessorType, _ResultProcessorType
from sqlalchemy.types import UserDefinedType


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

    def bind_processor(self, dialect: Dialect) -> _BindProcessorType[Address] | None:
        def process(value: Address | None) -> str | None:
            if value:
                return json.dumps(dataclasses.asdict(value))
            else:
                return None

        return process

    def result_processor(self, dialect: Dialect, coltype: object) -> _ResultProcessorType[Address] | None:
        def process(value: Any) -> Address | None:
            if value:
                # For asyncpg, `value` is a asyncpg.Record. Basically it's a tuple.
                return Address(**value)
            else:
                return None

        return process
