from enum import Enum, EnumType
import enum
import strawberry

@strawberry.type
class ValidationError:
    field: str
