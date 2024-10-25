from dataclasses import dataclass
from .period import Period
from .secondary_hours_type import SecondaryHoursType
from .special_day import SpecialDay

@dataclass
class OpeningHours:
    periods: list[Period]
    weekdayDescriptions: list[str]
    secondaryHoursType: SecondaryHoursType
    specialDays: list[SpecialDay]
    openNow: bool
