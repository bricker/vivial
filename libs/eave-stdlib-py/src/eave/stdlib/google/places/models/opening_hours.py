from typing import TypedDict

from .period import Period
from .secondary_hours_type import SecondaryHoursType
from .special_day import SpecialDay


class OpeningHours(TypedDict, total=False):
    periods: list[Period]
    weekdayDescriptions: list[str]
    secondaryHoursType: SecondaryHoursType
    specialDays: list[SpecialDay]
    openNow: bool
