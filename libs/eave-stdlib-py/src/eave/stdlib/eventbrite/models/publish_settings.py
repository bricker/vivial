from typing import TypedDict


class PublishSettings(TypedDict, total=False):
    """Event publish settings."""

    resource_uri: str | None
    """not documented"""

    published_date: str | None
    """not documented"""

    schedule_publish_date: str | None
    """not documented"""

    schedule_publish_status: str | None
    """not documented - an enum with "unscheduled" the only value I've seen."""

    can_publish: bool | None
    """not documented"""
