import dataclasses
import json
from dataclasses import dataclass
from typing import Any, Literal
from zoneinfo import ZoneInfo

from sqlalchemy import Dialect
from sqlalchemy.sql.type_api import _BindProcessorType, _ResultProcessorType
from sqlalchemy.types import UserDefinedType

from eave.stdlib.logging import LOGGER

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
            try:
                if value:
                    return json.dumps(dataclasses.asdict(value))
                else:
                    return None
            except Exception as e:
                LOGGER.exception(e)
                return None

        return process

    def result_processor(self, dialect: Dialect, coltype: object) -> _ResultProcessorType[Address] | None:
        def process(value: Any) -> Address | None:
            try:
                if value:
                    # For asyncpg, `value` is a asyncpg.Record. Basically it's a tuple.
                    # It's typed as "Any" because Record is defined in C and not available to the typing system.
                    return Address(**value)
                else:
                    return None
            except Exception as e:
                LOGGER.exception(e)
                return None

        return process

class ZoneInfoColumnType(UserDefinedType):
    cache_ok = True

    def get_col_spec(self) -> Literal["varchar"]:
        return "varchar"

    def bind_processor(self, dialect: Dialect) -> _BindProcessorType[ZoneInfo] | None:
        def process(value: ZoneInfo | None) -> str | None:
            try:
                if value:
                    return value.key
                else:
                    return None
            except Exception as e:
                LOGGER.exception(e)
                return None

        return process

    def result_processor(self, dialect: Dialect, coltype: object) -> _ResultProcessorType[ZoneInfo] | None:
        def process(value: Any) -> ZoneInfo | None:
            if value:
                # For asyncpg, `value` is a asyncpg.Record. Basically it's a tuple.
                # It's typed as "Any" because Record is defined in C and not available to the typing system.
                return ZoneInfo(**value)
            else:
                return None

        return process
