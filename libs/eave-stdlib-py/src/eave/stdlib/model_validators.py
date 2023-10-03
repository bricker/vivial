from typing import Any, Sized, TypeVar

import pydantic


T = TypeVar("T")
L = TypeVar("L", bound=Sized)


def validate_at_least_one_of(*fields: str) -> Any:
    def validate(cls, values: dict[str, Any]) -> dict[str, Any]:
        assert any(values.get(f) is not None for f in fields), f"At least one must be specified: {fields}"
        return values

    return pydantic.root_validator(allow_reuse=True, pre=False)(validate)


def validate_xnor(*fields: str) -> Any:
    def validate(cls, values: dict[str, Any]) -> dict[str, Any]:
        assert all(values.get(f) is None for f in fields) or all(values.get(f) is not None for f in fields)
        return values

    return pydantic.root_validator(allow_reuse=True)(validate)
