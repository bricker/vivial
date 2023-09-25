from typing import Any, Optional, Sized, TypeVar

import pydantic


T = TypeVar("T")
L = TypeVar("L", bound=Sized)


def validate_at_least_one_of(*fields: str) -> Any:
    def validate(self: T) -> T:
        assert any(getattr(self, f) is not None for f in fields), f"At least one must be specified: {fields}"
        return self

    return pydantic.root_validator(allow_reuse=True)(validate)

def validate_minimum_length(field: str, minimum_length: int) -> Any:
    def validate(cls: type, value: Optional[L]) -> Optional[L]:
        if value is None:
            return value

        assert len(value) > minimum_length
        return value

    return pydantic.validator(field, allow_reuse=True)(validate)

def validate_xnor(*fields: str) -> Any:
    def validate(self: T) -> T:
        assert all(getattr(self, f) is None for f in fields) or all(getattr(self, f) is not None for f in fields)
        return self

    return pydantic.root_validator(allow_reuse=True)(validate)
