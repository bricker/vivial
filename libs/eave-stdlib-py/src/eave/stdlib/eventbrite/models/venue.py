from typing import TypedDict


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


class Venue(TypedDict, total=False):
    """https://www.eventbrite.com/platform/api#/reference/venue"""

    id: str | None
    """Venue ID"""

    resource_uri: str | None

    name: str | None
    """Venue name"""

    age_restriction: str | None
    """Age restriction of the venue"""

    capacity: str | None
    """Venue capacity"""

    address: Address | None
    """The address of the venue"""

    latitude: str | None
    """Latitude coordinates of the Venue address."""

    longitude: str | None
    """Longitude coordinates of the Venue address."""
