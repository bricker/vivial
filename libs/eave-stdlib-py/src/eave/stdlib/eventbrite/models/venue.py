from typing import Required, TypedDict

from eave.stdlib.eventbrite.models.shared import Address


class Venue(TypedDict, total=False):
    """https://www.eventbrite.com/platform/api#/reference/venue"""

    id: str
    """Venue ID"""

    resource_uri: str

    name: Required[str]
    """Venue name"""

    age_restriction: str | None
    """Age restriction of the venue"""

    capacity: int | None
    """Venue capacity"""

    address: Address | None
    """The address of the venue"""

    latitude: str
    """Latitude coordinates of the Venue address."""

    longitude: str
    """Longitude coordinates of the Venue address."""
