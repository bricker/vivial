from dataclasses import dataclass
from types import MappingProxyType
from uuid import UUID


@dataclass(kw_only=True, frozen=True)
class ActivityFormatOrm:
    id: UUID
    name: str
    eventbrite_format_id: str

    @classmethod
    def all(cls) -> list["ActivityFormatOrm"]:
        return list(_ACTIVITY_FORMATS_TABLE)

    @classmethod
    def one_or_exception(cls, *, activity_format_id: UUID) -> "ActivityFormatOrm":
        return _ACTIVITY_FORMATS_PK[activity_format_id]

    @classmethod
    def get_by_eventbrite_id(cls, *, eventbrite_format_id: str) -> "ActivityFormatOrm | None":
        return _ACTIVITY_FORMATS_EBID_IDX.get(eventbrite_format_id)


_ACTIVITY_FORMATS_TABLE = (
    ActivityFormatOrm(
        id=UUID("095ce8e5e25e434c9e0c3fa395e29a01"),
        eventbrite_format_id="5",
        name="Festival",
    ),
    ActivityFormatOrm(
        id=UUID("169a3dadc7264664914edee5a98858a6"),
        eventbrite_format_id="6",
        name="Performance",
    ),
    ActivityFormatOrm(
        id=UUID("414b598c476d4f99bee99b801b42770a"),
        eventbrite_format_id="7",
        name="Screening",
    ),
    ActivityFormatOrm(
        id=UUID("2410b2f626af45379105b5a49dcaded6"),
        eventbrite_format_id="8",
        name="Gala",
    ),
    ActivityFormatOrm(
        id=UUID("e0d93e4443f8495998d33066226121b5"),
        eventbrite_format_id="9",
        name="Class",
    ),
    ActivityFormatOrm(
        id=UUID("dfa3ca339fef4b829feb2c76e55f0714"),
        eventbrite_format_id="11",
        name="Party",
    ),
    ActivityFormatOrm(
        id=UUID("8569443799a841b990d0e8d7373cd0fc"),
        eventbrite_format_id="13",
        name="Tournament",
    ),
    ActivityFormatOrm(
        id=UUID("d24a7552713c42f2962e863c406fcb59"),
        eventbrite_format_id="14",
        name="Game",
    ),
    ActivityFormatOrm(
        id=UUID("44a4ae2945944cfe96ba294c64418d05"),
        eventbrite_format_id="16",
        name="Tour",
    ),
    ActivityFormatOrm(
        id=UUID("f3f63bb6b1a448a99a56630d72b68666"),
        eventbrite_format_id="17",
        name="Attraction",
    ),
    ActivityFormatOrm(
        id=UUID("55c0e4589a3840798913881251264391"),
        eventbrite_format_id="100",
        name="Other",
    ),
)

_ACTIVITY_FORMATS_PK = MappingProxyType({fmt.id: fmt for fmt in _ACTIVITY_FORMATS_TABLE})
_ACTIVITY_FORMATS_EBID_IDX = MappingProxyType({fmt.eventbrite_format_id: fmt for fmt in _ACTIVITY_FORMATS_TABLE})
