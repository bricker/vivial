from typing import Any, Callable, Self, TypeVar

import pydantic


T = TypeVar("T")

def validate_at_least_one_of(*fields: str) -> Any:
    def validate(self: T) -> T:
        assert any(getattr(self, f) is not None for f in fields), f"At least one must be specified: {fields}"
        return self

    return pydantic.model_validator(mode="after")(validate)
