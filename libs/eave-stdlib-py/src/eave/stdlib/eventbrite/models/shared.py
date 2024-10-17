from typing import TypedDict


class CartesianCoordinates(TypedDict, total=False):
    x: int | None
    y: int | None


class MultipartText(TypedDict, total=False):
    """https://www.eventbrite.com/platform/api#/introduction/basic-types/multipart-text"""

    text: str | None
    html: str | None


class DatetimeWithTimezone(TypedDict, total=False):
    """https://www.eventbrite.com/platform/api#/introduction/basic-types/date-types"""

    timezone: str | None
    """A timezone value from the Olson specification"""

    utc: str | None
    """A datetime value in the UTC timezone"""

    local: str | None
    """A datetime value in the named timezone"""


class Price(TypedDict, total=False):
    """A dictionary with some data of the available ticket"""

    currency: str | None
    """The ISO 4217 3-character code of a currency"""

    value: int | None
    """The integer value of units of the minor unit of the currency (e.g. cents for US dollars)"""

    major_value: str | None
    """You can get a value in the currency's major unit - for example, dollars or pound sterling - by taking the integer value provided and shifting the decimal point left by the exponent value for that currency as defined in ISO 4217"""

    display: str | None
    """Provided for your convenience; its formatting may change depending on the locale you query the API with (for example, commas for decimal separators in European locales)."""
