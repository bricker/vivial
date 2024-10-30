from typing import TypedDict


class ParkingOptions(TypedDict, total=False):
    """https://developers.google.com/maps/documentation/places/web-service/reference/rest/v1/places#ParkingOptions"""

    freeParkingLot: bool
    paidParkingLot: bool
    freeStreetParking: bool
    paidStreetParking: bool
    valetParking: bool
    freeGarageParking: bool
    paidGarageParking: bool
