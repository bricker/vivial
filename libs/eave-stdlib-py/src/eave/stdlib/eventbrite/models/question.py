from typing import Required, TypedDict

from .shared import MultipartText


class Question(TypedDict, total=False):
    """https://www.eventbrite.com/platform/api#/reference/questions"""

    id: Required[str]
    """nodoc"""

    resource_uri: Required[str]
    """nodoc"""

    type: str | None
    """nodoc"""

    question: MultipartText | None
    """nodoc"""

    required: bool | None
    """nodoc"""

    include: bool | None
    """is this question enabled for the purchase flow"""

    editable: bool | None
    """is this question editable by the organizer"""

    choices: list[object] | None
    """nodoc"""

    ticket_classes: list[object] | None
    """nodoc"""

    group_id: str | None
    """nodoc - eg 'contact_information'"""

    group_display_header: str | None
    """nodoc"""

    respondent: str | None
    """nodoc - eg 'ticket_buyer'"""

    default_value: str | None
    """nodoc"""
