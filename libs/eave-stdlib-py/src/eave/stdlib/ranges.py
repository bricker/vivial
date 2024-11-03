from dataclasses import dataclass
from enum import StrEnum


class BoundInclusivity(StrEnum):
    """The enum values map to Postgres inclusivity syntax. See https://www.postgresql.org/docs/current/rangetypes.html#RANGETYPES-INCLUSIVITY"""
    EXCLUSIVE = "()"
    LOWER_ONLY = "[)"
    UPPER_ONLY = "(]"
    INCLUSIVE = "[]"

@dataclass
class BoundRange[T]:
    lower: T
    upper: T
