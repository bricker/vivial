import enum
import strawberry


@strawberry.enum
class EventSource(enum.Enum):
    INTERNAL = enum.auto()
    EVENTBRITE = enum.auto()
    GOOGLE_PLACES = enum.auto()
