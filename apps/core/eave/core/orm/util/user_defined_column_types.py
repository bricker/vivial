import dataclasses
import json
from abc import ABC, abstractmethod
from enum import IntEnum, StrEnum
from typing import Any, Literal, override
from zoneinfo import ZoneInfo

from sqlalchemy import Dialect
from sqlalchemy.sql.type_api import _BindProcessorType, _ResultProcessorType  # pyright: ignore [reportPrivateUsage]
from sqlalchemy.types import UserDefinedType

from eave.core.lib.address import Address
from eave.core.shared.enums import ActivitySource, OutingBudget, RestaurantSource
from eave.stdlib.exceptions import suppress_in_production


class AddressColumnType(UserDefinedType[Address]):
    cache_ok = True

    def get_col_spec(self) -> Literal["JSON"]:
        return "JSON"

    @override
    def bind_processor(self, dialect: Dialect) -> _BindProcessorType[Address] | None:
        def process(value: Address | None) -> str | None:
            with suppress_in_production(Exception):
                if value:
                    return json.dumps(dataclasses.asdict(value))

            return None

        return process

    @override
    def result_processor(self, dialect: Dialect, coltype: object) -> _ResultProcessorType[Address] | None:
        def process(value: dict[str, Any]) -> Address | None:
            with suppress_in_production(Exception):
                if value:
                    # For asyncpg, `value` is a asyncpg.Record. Basically it's a tuple.
                    # It's typed as "Any" because Record is defined in C and not available to the typing system.
                    return Address(**value)

            return None

        return process


class ZoneInfoColumnType(UserDefinedType[ZoneInfo]):
    cache_ok = True

    def get_col_spec(self) -> Literal["varchar"]:
        return "varchar"

    @override
    def bind_processor(self, dialect: Dialect) -> _BindProcessorType[ZoneInfo] | None:
        def process(value: ZoneInfo | None) -> str | None:
            with suppress_in_production(Exception):
                if value:
                    return value.key

            return None

        return process

    @override
    def result_processor(self, dialect: Dialect, coltype: object) -> _ResultProcessorType[ZoneInfo] | None:
        def process(value: str) -> ZoneInfo | None:
            with suppress_in_production(Exception):
                if value:
                    return ZoneInfo(value)

            return None

        return process


class StrEnumColumnType[T: StrEnum](UserDefinedType[T], ABC):
    cache_ok = True

    @abstractmethod
    def enum_member(self, value: str) -> T: ...

    def get_col_spec(self) -> Literal["varchar"]:
        return "varchar"

    @override
    def bind_processor(self, dialect: Dialect) -> _BindProcessorType[T] | None:
        def process(value: T | None) -> str | None:
            with suppress_in_production(Exception):
                if value:
                    return value.value

            return None

        return process

    @override
    def result_processor(self, dialect: Dialect, coltype: object) -> _ResultProcessorType[T] | None:
        def process(value: str) -> T | None:
            with suppress_in_production(Exception):
                if value:
                    # For asyncpg, `value` is a asyncpg.Record. Basically it's a tuple.
                    # It's typed as "Any" because Record is defined in C and not available to the typing system.
                    return self.enum_member(value)

            return None

        return process


class IntEnumColumnType[T: IntEnum](UserDefinedType[T], ABC):
    cache_ok = True

    @abstractmethod
    def enum_member(self, value: int) -> T: ...

    def get_col_spec(self) -> Literal["smallint"]:
        return "smallint"

    @override
    def bind_processor(self, dialect: Dialect) -> _BindProcessorType[T] | None:
        def process(value: T | None) -> int | None:
            with suppress_in_production(Exception):
                if value:
                    return value.value

            return None

        return process

    @override
    def result_processor(self, dialect: Dialect, coltype: object) -> _ResultProcessorType[T] | None:
        def process(value: int) -> T | None:
            with suppress_in_production(Exception):
                if value:
                    # For asyncpg, `value` is a asyncpg.Record. Basically it's a tuple.
                    # It's typed as "Any" because Record is defined in C and not available to the typing system.
                    return self.enum_member(value)

            return None

        return process


class ActivitySourceColumnType(StrEnumColumnType[ActivitySource]):
    cache_ok = True

    @override
    def enum_member(self, value: str) -> ActivitySource:
        return ActivitySource(value)


class RestaurantSourceColumnType(StrEnumColumnType[RestaurantSource]):
    cache_ok = True

    @override
    def enum_member(self, value: str) -> RestaurantSource:
        return RestaurantSource(value)


class OutingBudgetColumnType(IntEnumColumnType[OutingBudget]):
    cache_ok = True

    @override
    def enum_member(self, value: int) -> OutingBudget:
        return OutingBudget(value)
