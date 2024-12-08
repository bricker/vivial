from abc import abstractmethod, ABC
import dataclasses
from enum import EnumType, StrEnum
import json
from typing import Any, Literal, Type
from zoneinfo import ZoneInfo

from sqlalchemy import Dialect
from sqlalchemy.sql.type_api import _BindProcessorType, _ResultProcessorType
from sqlalchemy.types import UserDefinedType

from eave.stdlib.logging import LOGGER

from eave.core.shared.address import Address
from eave.core.shared.enums import ActivitySource, OutingBudget, RestaurantSource

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
        def process(value: dict[str, Any]) -> Address | None:
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
        def process(value: str) -> ZoneInfo | None:
            try:
                if value:
                    return ZoneInfo(value)
                else:
                    return None
            except Exception as e:
                LOGGER.exception(e)
                return None

        return process

class StrEnumColumnType[T: StrEnum](UserDefinedType, ABC):
    cache_ok = True

    @abstractmethod
    def enum_member(self, value: str) -> T:
        ...

    def get_col_spec(self) -> Literal["varchar"]:
        return "varchar"

    def bind_processor(self, dialect: Dialect) -> _BindProcessorType[T] | None:
        def process(value: T | None) -> str | None:
            try:
                if value:
                    return value.value
                else:
                    return None
            except Exception as e:
                LOGGER.exception(e)
                return None

        return process

    def result_processor(self, dialect: Dialect, coltype: object) -> _ResultProcessorType[T] | None:
        def process(value: str) -> T | None:
            try:
                if value:
                    # For asyncpg, `value` is a asyncpg.Record. Basically it's a tuple.
                    # It's typed as "Any" because Record is defined in C and not available to the typing system.
                    return self.enum_member(value)
                else:
                    return None
            except Exception as e:
                LOGGER.exception(e)
                return None

        return process

class ActivitySourceColumnType(StrEnumColumnType[ActivitySource]):
    def enum_member(self, value: str) -> ActivitySource:
        return ActivitySource[value]

class RestaurantSourceColumnType(StrEnumColumnType[RestaurantSource]):
    def enum_member(self, value: str) -> RestaurantSource:
        return RestaurantSource[value]

class OutingBudgetColumnType(StrEnumColumnType[OutingBudget]):
    def enum_member(self, value: str) -> OutingBudget:
        return OutingBudget[value]
