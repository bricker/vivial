from typing import TypedDict

from .shared import MultipartText


class Organizer(TypedDict, total=False):
    """not documented"""

    id: str | None
    """not documented"""

    resource_uri: str | None
    """not documented"""

    description: MultipartText | None
    """not documented"""

    long_description: MultipartText | None
    """not documented"""

    _type: str | None
    """not documented - 'organizer' is the only value I've seen"""

    name: str | None
    """not documented"""

    url: str | None
    """not documented"""

    num_past_events: int | None
    """not documented"""

    num_future_events: int | None
    """not documented"""

    organization_id: str | None
    """not documented"""

    disable_marketing_opt_in: bool | None
    """not documented"""

    logo_id: str | None
    """not documented"""
