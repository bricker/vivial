from typing import Required, TypedDict

from eave.stdlib.eventbrite.models.logo import Logo

from .shared import MultipartText


class Organizer(TypedDict, total=False):
    """not documented"""

    id: str
    """Id of the organizer"""

    resource_uri: str
    """Is an absolute URL to the API endpoint that will return you the organizer."""

    description: MultipartText
    """Description of the Organizer (may be very long and contain significant formatting)."""

    long_description: MultipartText
    """Long description of the Organizer."""

    name: str
    """Organizer name."""

    url: str
    """URL to the organizer's page on Eventbrite"""

    num_past_events: int
    """Number of past events the organizer has"""

    num_future_events: int
    """Number of upcoming events the organizer has"""

    logo_id: str | None
    """Image ID of the organizer logo"""

    logo: Logo | None
    """Full image details for organizer logo"""

    twitter: str
    """Organizer's twitter handle"""

    facebook: str
    """Organizer's facebook page"""

    _type: str | None
    """not documented - 'organizer' is the only value I've seen"""

    organization_id: str | None
    """not documented"""

    disable_marketing_opt_in: bool | None
    """not documented"""
