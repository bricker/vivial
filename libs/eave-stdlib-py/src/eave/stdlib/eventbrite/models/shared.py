from typing import Required, TypedDict


class CartesianCoordinates(TypedDict, total=True):
    x: int
    y: int


class MultipartText(TypedDict, total=True):
    """https://www.eventbrite.com/platform/api#/introduction/basic-types/multipart-text"""

    text: str
    html: str


class DatetimeWithTimezone(TypedDict, total=True):
    """https://www.eventbrite.com/platform/api#/introduction/basic-types/date-types"""

    timezone: str
    """A timezone value from the Olson specification"""

    utc: str
    """A datetime value in the UTC timezone"""

    local: str
    """A datetime value in the named timezone"""


class CurrencyCost(TypedDict, total=True):
    """A dictionary with some data of the available ticket"""

    currency: str
    """The ISO 4217 3-character code of a currency"""

    value: int
    """The integer value of units of the minor unit of the currency (e.g. cents for US dollars)"""

    major_value: str
    """You can get a value in the currency's major unit - for example, dollars or pound sterling - by taking the integer value provided and shifting the decimal point left by the exponent value for that currency as defined in ISO 4217"""

    display: str
    """Provided for your convenience; its formatting may change depending on the locale you query the API with (for example, commas for decimal separators in European locales)."""


class Address(TypedDict, total=False):
    """https://www.eventbrite.com/platform/api#/introduction/basic-types/address"""

    address_1: str | None
    """The street/location address (part 1)"""

    address_2: str | None
    """The street/location address (part 2)"""

    city: str | None
    """City"""

    region: str | None
    """ISO 3166-2 2- or 3-character region code for the state, province, region, or district"""

    postal_code: str | None
    """Postal code"""

    country: str | None
    """ISO 3166-1 2-character international code for the country"""

    latitude: str | None
    """Latitude portion of the address coordinates"""

    longitude: str | None
    """Longitude portion of the address coordinates"""

    localized_address_display: str | None
    """The format of the address display localized to the address country"""

    localized_area_display: str | None
    """The format of the address's area display localized to the address country"""

    localized_multi_line_address_display: list[str] | None
    """The multi-line format order of the address display localized to the address country, where each line is an item in the list"""


class Image(TypedDict, total=True):
    id: Required[str]
    """The image's ID"""

    url: Required[str]
    """The URL of the image"""
