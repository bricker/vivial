import strawberry

from eave.core.outing.models.sources import ActivitySource

from .location import Location
from .photos import Photos


@strawberry.type
class ActivityTicketInfo:
    type: str | None
    notes: str | None
    cost: int | None = 0
    fee: int | None = 0
    tax: int | None = 0


@strawberry.type
class ActivityVenue:
    name: str
    location: Location


@strawberry.type
class Activity:
    source: ActivitySource
    ticket_info: ActivityTicketInfo
    venue: ActivityVenue
    photos: Photos
    name: str
    description: str
    website_uri: str | None
    door_tips: str | None
    insider_tips: str | None
    parking_tips: str | None
