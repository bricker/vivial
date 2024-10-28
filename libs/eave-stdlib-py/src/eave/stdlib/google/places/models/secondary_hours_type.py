from enum import StrEnum


class SecondaryHoursType(StrEnum):
    """https://developers.google.com/maps/documentation/places/web-service/reference/rest/v1/places#SecondaryHoursType"""

    SECONDARY_HOURS_TYPE_UNSPECIFIED = "SECONDARY_HOURS_TYPE_UNSPECIFIED"
    DRIVE_THROUGH = "DRIVE_THROUGH"
    HAPPY_HOUR = "HAPPY_HOUR"
    DELIVERY = "DELIVERY"
    TAKEOUT = "TAKEOUT"
    KITCHEN = "KITCHEN"
    BREAKFAST = "BREAKFAST"
    LUNCH = "LUNCH"
    DINNER = "DINNER"
    BRUNCH = "BRUNCH"
    PICKUP = "PICKUP"
    ACCESS = "ACCESS"
    SENIOR_HOURS = "SENIOR_HOURS"
    ONLINE_SERVICE_HOURS = "ONLINE_SERVICE_HOURS"
