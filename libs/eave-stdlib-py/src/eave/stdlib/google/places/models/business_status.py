from enum import StrEnum


class BusinessStatus(StrEnum):
    """https://developers.google.com/maps/documentation/places/web-service/reference/rest/v1/places#BusinessStatus"""

    BUSINESS_STATUS_UNSPECIFIED = "BUSINESS_STATUS_UNSPECIFIED"
    OPERATIONAL = "OPERATIONAL"
    CLOSED_TEMPORARILY = "CLOSED_TEMPORARILY"
    CLOSED_PERMANENTLY = "CLOSED_PERMANENTLY"
