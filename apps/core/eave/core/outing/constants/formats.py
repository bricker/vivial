
from uuid import UUID

from eave.stdlib.logging import LOGGER

from eave.core.outing.models.category import ActivityFormat


ACTIVITY_FORMATS = [
    ActivityFormat(
        id=UUID("095ce8e5e25e434c9e0c3fa395e29a01"),
        eventbrite_format_id="5",
        name="Festival",
    ),
    ActivityFormat(
        id=UUID("169a3dadc7264664914edee5a98858a6"),
        eventbrite_format_id="6",
        name="Performance",
    ),
    ActivityFormat(
        id=UUID("414b598c476d4f99bee99b801b42770a"),
        eventbrite_format_id="7",
        name="Screening",
    ),
    ActivityFormat(
        id=UUID("2410b2f626af45379105b5a49dcaded6"),
        eventbrite_format_id="8",
        name="Gala",
    ),
    ActivityFormat(
        id=UUID("e0d93e4443f8495998d33066226121b5"),
        eventbrite_format_id="9",
        name="Class",
    ),
    ActivityFormat(
        id=UUID("dfa3ca339fef4b829feb2c76e55f0714"),
        eventbrite_format_id="11",
        name="Party",
    ),
    ActivityFormat(
        id=UUID("8569443799a841b990d0e8d7373cd0fc"),
        eventbrite_format_id="13",
        name="Tournament",
    ),
    ActivityFormat(
        id=UUID("d24a7552713c42f2962e863c406fcb59"),
        eventbrite_format_id="14",
        name="Game",
    ),
    ActivityFormat(
        id=UUID("44a4ae2945944cfe96ba294c64418d05"),
        eventbrite_format_id="16",
        name="Tour",
    ),
    ActivityFormat(
        id=UUID("f3f63bb6b1a448a99a56630d72b68666"),
        eventbrite_format_id="17",
        name="Attraction",
    ),
    ActivityFormat(
        id=UUID("55c0e4589a3840798913881251264391"),
        eventbrite_format_id="100",
        name="Other",
    ),
]

_EB_FORMATS_TO_VIVIAL: dict[str, ActivityFormat] = {}
"""
A map of { "eventbrite_format_id" => "vivial_format_id" }
"""

for fmt in ACTIVITY_FORMATS:
    for ebid in fmt.eventbrite_format_id:
        if ebid in _EB_FORMATS_TO_VIVIAL:
            LOGGER.warning(f"Duplicate eventbrite_format_id found: {ebid}")

        _EB_FORMATS_TO_VIVIAL[ebid] = fmt

def get_vivial_format_from_eventbrite_format_id(eventbrite_format_id: str) -> ActivityFormat | None:
    return _EB_FORMATS_TO_VIVIAL.get(eventbrite_format_id)
